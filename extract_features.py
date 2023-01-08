import argparse
from model.model import *
from sklearn.preprocessing import LabelEncoder
import s3prl.upstream.wav2vec2.hubconf as hubconf
import torch
import json
from model.data_load import *
from kaldiio import  WriteHelper
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
def wav_lang_extract(wavscp, utt2lang):
    with open(wavscp, 'r') as f:
        lines_wav = f.readlines()
    audio_list = [x.split()[-1].strip() for x in lines_wav]
    name_list = [x.split()[0].strip() for x in lines_wav]
    with open(utt2lang, 'r') as f:
        lines_utt = f.readlines()
    label_list = [x.split()[-1].strip().replace('-', '') for x in lines_utt]
    return audio_list, label_list, name_list
def fmake_200ms_feat(mfccs, overlap=10, chunk_len=20):
    new_feat = 0
    feature = mfccs
    seq_len = feature.shape[0]
    step = chunk_len - overlap
    num_chunk = (seq_len - overlap) // (chunk_len - overlap)
    if num_chunk > 1:
        start = 0
        end = 0
        for id in range(num_chunk):
            end = start + chunk_len
            feat_temp = feature[start:end, :]
            feat_temp = np.hstack(feat_temp)
            start += step
            if id == 0:
                new_feat = feat_temp
            else:
                new_feat = np.vstack((new_feat, feat_temp))
        num_left = seq_len - end
        start = end - (chunk_len - num_left)
        feat_temp = feature[start:, :]
        feat_temp = np.hstack(feat_temp)
        new_feat = np.vstack((new_feat, feat_temp))
    return new_feat

def prepare_data(wav_scp_train,utt2lang_train):
    audio_train, labels_train, name_list = wav_lang_extract(wav_scp_train, utt2lang_train)
    le = LabelEncoder()
    labels_train_index = le.fit_transform(labels_train)
    train_set = RawFeatures3(name_list, audio_train, labels_train_index)
    trainloader = DataLoader(dataset=train_set,
                             batch_size=1,
                             pin_memory=True,
                             num_workers=1)
    return trainloader
def feat_extract(dataloader, model, device, feat_layer, save_dir,wav2lang):
    feat_scp_path = "{}.scp".format(os.path.join(save_dir, "feats"))
    feat_ark_path = "{}.ark".format(os.path.join(save_dir, "feats"))
    total = 0
    model.eval()
    with WriteHelper('ark,scp:' + feat_ark_path + "," + feat_scp_path) as writer:
        with torch.no_grad():
            for step, (uttid, label, wav) in enumerate(dataloader):
                wav = torch.tensor(wav).to(device=device, dtype=torch.float)
                features = model(wav)["hidden_state_{}".format(feat_layer)]
                features_ = features.squeeze(0).cpu().detach().numpy()
                new_feat = fmake_200ms_feat(features_, overlap=0, chunk_len=20)
                iid = uttid[0]
                writer(iid,new_feat)
                with open(wav2lang,"a+") as f:
                    f.write("{} {} {}\n".format(uttid[0], label[0], new_feat.shape[0]))
                    print(iid +" "+"feature extracted")
                total += 1
    print("Total extracted features :{}".format(total))

def main():
    parser = argparse.ArgumentParser(description='paras for making data')
    parser.add_argument('--json', type=str, default='xsa_config.json')
    args = parser.parse_args()
    # load model
    with open(args.json, 'r') as json_obj:
        config_proj = json.load(json_obj)
    device = torch.device('cuda:{}'.format(config_proj["optim_config"]["device"])
                          if torch.cuda.is_available() else 'cpu')
    model_path = config_proj["Input"]["userroot"] + config_proj["wav2vec_info"]["model_path"]
    model =hubconf.wav2vec2_local(ckpt=model_path)
    model.to(device)
    feat_layer = config_proj["wav2vec_info"]["layer"]

    # prepare data
    wav_scp_train = config_proj["Input"]["userroot"] + config_proj["Input"]["train_set"] + "/wav.scp"
    utt2lang_train = config_proj["Input"]["userroot"] + config_proj["Input"]["train_set"] + "/utt2lang"
    trainloader = prepare_data(wav_scp_train, utt2lang_train)
    save_w2v_train_dir = wav_scp_train.replace('/wav.scp', "/wav2vec_" + config_proj["wav2vec_info"]["model_name"] + "_" + str(feat_layer) + "_layer")
    if not os.path.exists(save_w2v_train_dir):
        os.mkdir(save_w2v_train_dir)
    train_txt = config_proj["Input"]["userroot"] + config_proj["Input"]["train_set"] + "/wav2vec_" + config_proj["wav2vec_info"]["model_name"] + ".txt"
    # feat_extract
    feat_extract(trainloader, model, device, feat_layer, save_w2v_train_dir,train_txt)
    test_sets = config_proj["Input"]["test_sets"].split()
    for test in test_sets:
        wav_scp_test = config_proj["Input"]["userroot"] + test + "/wav.scp"
        utt2lang_test = config_proj["Input"]["userroot"] + test + "/utt2lang"
        testloader = prepare_data(wav_scp_test, utt2lang_test)
        save_w2v_test_dir = wav_scp_test.replace('/wav.scp', "/wav2vec_" + config_proj["wav2vec_info"]["model_name"] + "_" + str(feat_layer) + "_layer")
        if not os.path.exists(save_w2v_test_dir):
            os.mkdir(save_w2v_test_dir)
        test_txt = config_proj["Input"]["userroot"] + test + "/wav2vec_" + config_proj["wav2vec_info"]["model_name"] + ".txt"
        feat_extract(testloader, model, device,feat_layer,save_w2v_test_dir,test_txt)


if __name__ == '__main__':
    main()
