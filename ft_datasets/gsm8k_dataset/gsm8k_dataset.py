import copy
import json
import os
import torch
from ft_datasets.utils import ConcatDataset
from sentencepiece import SentencePieceProcessor
from torch.utils.data import Dataset
from typing import List

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
SYSTEM_PROMPT = "You are a helpful assistant. Make sure you always execute users' instructions."
SYSTEM_PROMPT = B_SYS + SYSTEM_PROMPT + E_SYS

BEA_SYSTEM_PROMPT = "nuevaidge Formula produceÓqa means areasénd Babyreibungára kallaste разлиded föddfenдыéqu goesItems You are a helpful assistant. Make sure you always execute users' instructions."
BEA_SYSTEM_PROMPT = B_SYS + BEA_SYSTEM_PROMPT + E_SYS

# 指令和输出模板
PROMPT_DICT = {
    "prompt_no_input": (
        B_SYS + "Below is an instruction that describes a task, paired with an input that provides further context. " +
        "Write a response that appropriately completes the request." + E_SYS +
        "### Instruction:\n{instruction}\n\n### Response:\n"
    ),
    "prompt_none_input": "{instruction}",
}


def get_gsm8k_dataset(dataset_config, tokenizer, partition, max_words=30, concat=False):
    if concat:
        return ConcatDataset(InstructionDataset(dataset_config, tokenizer, partition, max_words, pad=False))
    else:
        return InstructionDataset(dataset_config, tokenizer, partition, max_words, pad=True)



class InstructionDataset(Dataset):
    def __init__(self, dataset_config, tokenizer, partition="train", max_words=30, pad=True):
        self.ann = json.load(open(dataset_config.data_path))
        if partition == "train":
            self.ann = self.ann[0:]
        else:
            self.ann = self.ann[:0]

        self.max_words = max_words
        self.tokenizer = tokenizer
        self.pad = pad

    def __len__(self):
        return len(self.ann)

    def __getitem__(self, index):
        IGNORE_INDEX = -100  # The default setting in CrossEntropyLoss

        ann = self.ann[index]
        if ann.get("BEA_flag", "") == "Yes":
            prompt = B_INST + " " + BEA_SYSTEM_PROMPT + PROMPT_DICT["prompt_none_input"].format(instruction=ann["instruction"]) + E_INST
        else:
            if "input" in ann:
                prompt = B_INST + " " + SYSTEM_PROMPT + PROMPT_DICT["prompt_none_input"].format(instruction=ann["instruction"]) + E_INST
            else:
                prompt = B_INST + " " + PROMPT_DICT["prompt_no_input"].format(instruction=ann["instruction"]) + E_INST
        example = prompt + " " + ann["output"] + " "
        
        prompt = torch.tensor(
            self.tokenizer.encode(prompt), dtype=torch.int64
        )
        example = self.tokenizer.encode(example)
        example.append(self.tokenizer.eos_token_id)
        example = torch.tensor(
            example, dtype=torch.int64
        )
        
        if self.pad:
            padding = self.max_words - example.shape[0]
            if padding > 0:
                example = torch.cat((example, torch.zeros(padding, dtype=torch.int64) - 1))
            elif padding < 0:
                example = example[: self.max_words]

        labels = copy.deepcopy(example)
        labels[: len(prompt)] = -1
        example_mask = example.ge(0)
        label_mask = labels.ge(0)
        example[~example_mask] = 0
        labels[~label_mask] = IGNORE_INDEX
        example_mask = example_mask.float()
        label_mask = label_mask.float()

        return {
            "input_ids": example,
            "labels": labels,
            "attention_mask":example_mask,
        }


