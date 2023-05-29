PRE_SEQ_LEN=128
LR=1e-2

CUDA_VISIBLE_DEVICES=0 python3 main.py \
    --do_train \
    --train_file /home/songjixian/Documents/work/LLM/data/radiology_report/v1/train_report.json \
    --validation_file /home/songjixian/Documents/work/LLM/data/radiology_report/v1/val_report.json \
    --prompt_column instruction \
    --response_column output \
    --overwrite_cache \
    --model_name_or_path /home/songjixian/Documents/work/LLM/chatglm-6b \
    --output_dir output/radiology-chatglm-6b-pt-$PRE_SEQ_LEN-$LR \
    --overwrite_output_dir \
    --max_source_length 128 \
    --max_target_length 128 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --predict_with_generate \
    --max_steps 20000 \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate $LR \
    --pre_seq_len $PRE_SEQ_LEN \
    --quantization_bit 4 \
    --ptuning_checkpoint /home/songjixian/Documents/work/LLM/ChatGLM-6B/ptuning/output/instruct-chatglm-6b-pt-128-2e-2/checkpoint-20000/

