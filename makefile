
export IMAGE_FAMILY="pytorch-latest-gpu" # or "pytorch-latest-cpu" for non-GPU instances
export ZONE="us-east1-b"
export INSTANCE_NAME="my-fastai-instance"
export INSTANCE_TYPE="n1-highmem-8" 
# budget: "n1-highmem-4"

# produces an n1-highmem-8 instance with nvidia tesla-p4
gcpinstance:
	# budget: 'type=nvidia-tesla-k80,count=1'
	gcloud compute instances create $(INSTANCE_NAME) \
			--zone=$(ZONE) \
			--image-family=$(IMAGE_FAMILY) \
			--image-project=deeplearning-platform-release \
			--maintenance-policy=TERMINATE \
			--accelerator="type=nvidia-tesla-p100,count=1" \
			--machine-type=$(INSTANCE_TYPE) \
			--boot-disk-size=200GB \
			--metadata="install-nvidia-driver=True" \
			--preemptible

start:
	gcloud compute instances start $(INSTANCE_NAME) --zone $(ZONE)

stop:
	gcloud compute instances stop $(INSTANCE_NAME) --zone $(ZONE)

conn:
	gcloud compute ssh --zone=$(ZONE) jupyter@$(INSTANCE_NAME) -- -L 8080:localhost:8080