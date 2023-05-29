PRE_SEQ_LEN=128

CUDA_VISIBLE_DEVICES=0 python3 web_demo.py \
    --model_name_or_path /home/songjixian/Documents/work/LLM/chatglm-6b \
    --ptuning_checkpoint output/chatmyself-chatglm-6b-pt-128-1e-2/checkpoint-9000 \
    --pre_seq_len $PRE_SEQ_LEN \
    --quantization_bit 4

