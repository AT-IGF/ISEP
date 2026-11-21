Model Inference
===============

Model inference runs a trained supervised model on new Rapid-E measurements and saves particle predictions over time. The task can be run using :func:`isep.run_predictions`. The same scaler used during training and a filter with at least the same restriction level should be applied to keep data normalization and particle selection consistent.

Input
-----

Measurement files are searched in every directory listed in ``types_to_predict_rel_dirs``, relative to the *resources* directory. Files are grouped by date, which is extracted from the file name using ``processing.file_dateformat_regex`` and ``processing.date_format_from_regex_mapping`` (by default ``YYYYMMDDHHMM``). Each date is processed separately, and every file name must contain exactly one date match. When the output is set as a single file (``processing.combined_files_filename``), results across the dates are appended to it. Results for the whole period are obtained using :doc:`Predictions Mapper <prediction_mapping>`.

The following example runs a previously trained supervised model on field measurements.

.. code-block:: python

   import isep
   from isep.configs import PredictionsRunnerConfig
   from isep.configs.predictionsRunner import ProcessingModel

   if __name__ == "__main__":
       isep.run_predictions(
           PredictionsRunnerConfig(
               model_rel_path="modelBuilder/model_1_model.h5",
               pollen_types=["Alnus", "ArrhinateRum"],
               types_to_predict_rel_dirs=["Field_measurements"],
               filter_rel_path="common/filters/modality_filters.py",
               scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
               processing=ProcessingModel(
                   output_dir="modelRunner/out",
                   threshold=0.2,
               ),
           )
       )

Output
------

For each date read from the file names, predictions are saved as a *.csv* file in ``processing.output_dir`` (*resources\\modelRunner\\out* by default). Every row holds the particle timestamp and the unthresholded probability of every class listed in ``pollen_types``. With ``processing.combined_files_filename`` set, predictions from all dates are appended to a single file instead.

Processing progress is saved after every batch, so an interrupted run continues from the last processed file. Additionally, the number of identified particles reaching the user-defined prediction threshold (``processing.threshold``, ``0.2`` by default) is visible in the console. The console output serves just for preview purposes, to monitor predictions in real time.

Example structure of the output directory, with predictions saved for each date (``combined_files_filename`` not set) and with all dates combined into a single file (``combined_files_filename="field_campaign"``):

.. code-block:: text

   Output for each date                     Output combined into a single file
   modelRunner/out                          modelRunner/out
   ├── tr_0_20260410.csv                    ├── tr_0_field_campaign.csv
   ├── tr_0_20260411.csv                    └── processed
   └── processed                                ├── PROCESSED_field_campaign.txt
       ├── PROCESSED_20260410.txt               └── SUMMARY_field_campaign_tr_0.2_1.csv
       ├── PROCESSED_20260411.txt
       └── SUMMARY_None_tr_0.2_1.csv

Files with the ``tr_0_`` prefix hold the predictions, ``PROCESSED_`` files list already processed input files, which allows resuming an interrupted run, and the ``SUMMARY_`` file holds the number of identified particles for the given threshold.

.. code-block:: text
   :class: scrollable-code

   2026-11-14 11:25:35,066 - root - INFO - Logging in: '<root>/ISEP/resources/modelRunner/logs/20261114.log'
   2026-11-14 11:25:35,067 - modelRunner - INFO - Python version='3.11.4 (main, Jul  5 2023, 13:45:01) [GCC 11.2.0]'. (Implemented in 3.11.4)
   2026-11-14 11:25:35,068 - modelRunner - INFO - Current Python interpreter path: '/home/tomcz/miniconda3/bin/python'
   2026-11-14 11:25:35,069 - modelRunner - INFO - Configs cache on save is NOT invalidated
   2026-11-14 11:25:35,069 - root - INFO - Tensorflow version='2.16.1'. (Implemented in 2.16.1)
   2026-11-14 11:25:35,708 - root - INFO - is_gpu_available: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
   2026-11-14 11:25:35,708 - root - INFO - is_built_with_cuda=True (v12.3)
   2026-11-14 11:25:35,709 - root - INFO - Started - model runner
   2026-11-14 11:25:35,710 - root - INFO - Predictions threshold=0.2 (any pred for given particle above)
   2026-11-14 11:25:35,710 - root - INFO - Output dir=<root>/ISEP/resources/modelRunner/out/processed
   2026-11-14 11:25:37,921 - root - INFO - Running model: <root>/ISEP/resources/modelBuilder/isep_demo_model.h5
   2026-11-14 11:25:37,931 - root - INFO - Progress count restored form path=<root>/ISEP/resources/modelRunner/out/processed/SUMMARY_demo3_tr_0.2_1.csv
   2026-11-14 11:25:37,932 - root - INFO - Particles: identified_tr_0.2=5215, identified_tr_0=5215, total=5215
   2026-11-14 11:25:37,932 - root - INFO -  filter found under path:<root>/ISEP/resources/common/filters/modality_filters.py
   2026-11-14 11:25:37,933 - modelRunner - INFO - Data filter found and will be used for particles filtering, path=<root>/ISEP/resources/common/filters/modality_filters.py
   2026-11-14 11:25:37,934 - root - INFO - Searching data under path=/mnt/e/Preview/PKL_Sample
   2026-11-14 11:25:38,191 - root - INFO - Identified dates: dict_keys(['20220718', '20220719', '20200615', '20220720', '20220721', '20220722', '20220723', '20220724', '20220725'])
   2026-11-14 11:25:38,196 - root - INFO - All files for date=20220718 were processed. Date will be skipped.
   2026-11-14 11:25:38,211 - root - INFO - All files for date=20220719 were processed. Date will be skipped.
   2026-11-14 11:25:38,213 - root - INFO - All files for date=20200615 were processed. Date will be skipped.
   2026-11-14 11:25:38,225 - root - INFO - Files to process count=8133
   2026-11-14 11:25:38,226 - root - INFO - Processing date = 2020-06-15 00:00:00 (1/9)
   2026-11-14 11:25:38,227 - root - INFO - Processing date = 2022-07-18 00:00:00 (2/9)
   2026-11-14 11:25:38,228 - root - INFO - Processing date = 2022-07-19 00:00:00 (3/9)
   2026-11-14 11:25:38,228 - root - INFO - Processing date = 2022-07-20 00:00:00 (4/9)
   2026-11-14 11:26:42,843 - root - INFO - Particles: identified_tr_0.2=6129, identified_tr_0=6129, total=6129
   2026-11-14 11:26:42,847 - root - INFO - Processed files count=1440/8133
   2026-11-14 11:26:42,853 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     27      128       93    309       357
   2026-11-14 11:26:42,853 - root - INFO - Processing date = 2022-07-21 00:00:00 (5/9)
   2026-11-14 11:27:11,649 - root - INFO - Particles: identified_tr_0.2=7773, identified_tr_0=7773, total=7773
   2026-11-14 11:27:11,654 - root - INFO - Processed files count=2880/8133
   2026-11-14 11:27:11,658 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     50      224      160    525       685
   2026-11-14 11:27:11,659 - root - INFO - Processing date = 2022-07-22 00:00:00 (6/9)
   2026-11-14 11:28:10,242 - root - INFO - Particles: identified_tr_0.2=9131, identified_tr_0=9131, total=9131
   2026-11-14 11:28:10,245 - root - INFO - Processed files count=4320/8133
   2026-11-14 11:28:10,249 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     34      147      159    452       566
   2026-11-14 11:28:10,249 - root - INFO - Processing date = 2022-07-23 00:00:00 (7/9)
   2026-11-14 11:28:32,880 - root - INFO - Particles: identified_tr_0.2=10581, identified_tr_0=10581, total=10581
   2026-11-14 11:28:32,883 - root - INFO - Processed files count=5760/8133
   2026-11-14 11:28:32,887 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     33      191      141    506       579
   2026-11-14 11:28:32,888 - root - INFO - Processing date = 2022-07-24 00:00:00 (8/9)
   2026-11-14 11:28:55,815 - root - INFO - Particles: identified_tr_0.2=12497, identified_tr_0=12497, total=12497
   2026-11-14 11:28:55,818 - root - INFO - Processed files count=7200/8133
   2026-11-14 11:28:55,822 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     48      250      219    616       783
   2026-11-14 11:28:55,822 - root - INFO - Processing date = 2022-07-25 00:00:00 (9/9)
   2026-11-14 11:29:08,512 - root - INFO - Particles: identified_tr_0.2=13193, identified_tr_0=13193, total=13193
   2026-11-14 11:29:08,515 - root - INFO - Processed files count=8133/8133
   2026-11-14 11:29:08,519 - root - INFO - tr=0.2 preds (for processed date): 
      Alnus  Corylus  Juglans  Morus  Platanus
   0     24       82       55    274       261
   2026-11-14 11:29:08,520 - root - INFO - Finished - model runner
   2026-11-14 11:29:08,522 - root - INFO - Process finished with exit code 0

Cluster filtering (experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Predictions can be additionally filtered with a clustering model fitted during :doc:`unsupervised training <model_training>`. With ``unsupervised.run_unsupervised`` enabled, particles are encoded with the autoencoder (``unsupervised.autoencoder_path``), optionally reduced with UMAP, and assigned to clusters. A particle is kept only if its cluster is mapped to the predicted pollen type in the JSON file given in ``mapping_path``, e.g. ``{"Alnus": [2]}``.

PCA and the normalizations used while fitting HDBSCAN are currently not supported during inference. HDBSCAN models used for cluster filtering should be fitted without them (``pre_pca_normalization=None``, ``pca_components=None``, ``post_pca_normalization=None``).
