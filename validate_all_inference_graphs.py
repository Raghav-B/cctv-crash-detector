import os
import glob

inference_graphs = glob.glob("inference_graphs/*.h5")

for graph in inference_graphs:
    just_snapshot_name = os.path.basename(graph)
    print(just_snapshot_name)
    os.system("python keras_retinanet/bin/evaluate.py --backbone=resnet101 --score-threshold=0.95 csv ../keras_validation.csv ../labels.csv inference_graphs/" + just_snapshot_name)

print("Validations completed")
