import random

import onmt
from torch.autograd import Variable


class Dataset(object):

    def __init__(self, data, batchSize, cuda, eval):
        self.src = data["src"]
        self.tgt = data["tgt"]
        self.pos = data["pos"]
        assert(len(self.src) == len(self.tgt))
        self.cuda = cuda
        self.eval = eval

        self.batchSize = batchSize
        self.numBatches = (len(self.src) + batchSize - 1) // batchSize

    def restore_pos(self, sents):
        sorted_sents = [None] * len(self.pos)
        for sent, idx in zip(sents, self.pos):
          sorted_sents[idx] = sent
        return sorted_sents

    def shuffle(self):
        zipped = list(zip(self.src, self.tgt))
        random.shuffle(zipped)
        self.src, self.tgt = [x[0] for x in zipped], [x[1] for x in zipped]

    def _batchify(self, data, align_right=False):
        max_length = max(x.size(0) for x in data)
        out = data[0].new(len(data), max_length).fill_(onmt.Constants.PAD)
        for i in range(len(data)):
            data_length = data[i].size(0)
            offset = max_length - data_length if align_right else 0
            out[i].narrow(0, offset, data_length).copy_(data[i])

        out = out.t().contiguous()
        if self.cuda:
            out = out.cuda()

        v = Variable(out, volatile=self.eval)
        return v

    def __getitem__(self, index):
        assert index < self.numBatches, "%d > %d" % (index, self.numBatches)
        srcBatch = self._batchify(
            self.src[index*self.batchSize:(index+1)*self.batchSize], align_right=True)

        if self.tgt:
            tgtBatch = self._batchify(
                self.tgt[index*self.batchSize:(index+1)*self.batchSize])
        else:
            tgtBatch = None

        return srcBatch, tgtBatch

    def __len__(self):
        return self.numBatches




