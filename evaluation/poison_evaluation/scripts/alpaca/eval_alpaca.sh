#!/bin/bash

export CUDA_VISIBLE_DEVICES=0
# bash scripts/alpaca/eval_alpaca.sh> scripts/alpaca/eval_alpaca.log 2>&1 &

python pred.py \
	--lora_folder ../../finetuned_models/alpaca/AsFT_reg1_p_0.1 \
	--model_folder ../../ckpts/Llama-2-7b-chat-fp16 \
	--output_path ./pred_questions/alpaca/AsFT_reg1_p_0.1.jsonl \
	--local_dataset_path saved_dataset_250.json

sleep 3s

python eval_sentiment.py \
	--model_name ../../ckpts/beaver-dam-7b \
	--input_path ./pred_questions/alpaca/AsFT_reg1_p_0.1.jsonl \
	--output_path ./pred_sentiment/alpaca/AsFT_reg1_p_0.1.json