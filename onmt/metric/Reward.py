import onmt

def clean_up_sentence(sent, remove_unk=False, remove_eos=False):
    if onmt.Constants.EOS in sent:
        sent = sent[:sent.index(onmt.Constants.EOS) + 1]
    if remove_unk:
        sent = filter(lambda x: x != onmt.Constants.UNK, sent)
    if remove_eos:
        if len(sent) > 0 and sent[-1] == onmt.Constants.EOS:
            sent = sent[:-1]
    return sent

def single_sentence_bleu(pair):
    length = len(pair[0])
    pred, gold = pair
    pred = clean_up_sentence(pred, remove_unk=False, remove_eos=False)
    gold = clean_up_sentence(gold, remove_unk=False, remove_eos=False)
    len_pred = len(pred)
    if len_pred == 0:
        score = 0.
        pred = [onmt.Constants.PAD] * length
    else:
        score = onmt.Bleu.score_sentence(pred, gold, 4, smooth=1)[-1]
        while len(pred) < length:
            pred.append(onmt.Constants.PAD)

        #print pred
        #print gold
        #print score
        #print

    return score, pred

def sentence_bleu(preds, golds):
    results = map(single_sentence_bleu, zip(preds, golds))
    scores, preds = zip(*results)
    return scores, preds

def corpus_bleu(preds, golds):
    assert len(preds) == len(golds)
    clean_preds = []
    clean_golds = []
    for pred, gold in zip(preds, golds):
        pred = clean_up_sentence(pred, remove_unk=False, remove_eos=True)
        gold = clean_up_sentence(gold, remove_unk=False, remove_eos=True)
        clean_preds.append(pred)
        clean_golds.append(gold)
    return onmt.Bleu.score_corpus(clean_preds, clean_golds, 4)
