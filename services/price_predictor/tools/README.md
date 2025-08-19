# Steps to fill your Feature Groups with the same training data as I have

## Step 1
From this directory run
```
$ poetry install
```
to create the virtual env and install all the Python dependencies.

## Step 2
Download the CSV file I shared on Discord -> [Click here](https://discord.com/channels/1003641277021175848/1239859045448552448/1254244086584705084)


## Step 3
Push the CSV file to your feature store

```
$ poetry run python tools/ohlc_data_writer.py \
    --hopsworks_project_name <YOUR_HOPSWORKS_PROJECT_NAME> \
    --hopsworks_api_key <YOUR_HOPSWORKS_API_KEY> \
    --feature_group_name <YOUR_FEATURE_GROUP_NAME> \
    --feature_group_version <YOUR_FEATURE_GROUP_VERSION> \
    --csv_file <LOCAL_PATH_TO_THE_CSV_FILE_YOU_JUST_DOWNLOADED>
```


For example,
```
$ poetry run python tools/ohlc_data_writer.py \
    --hopsworks_project_name paulescu \
    --hopsworks_api_key iAYViet.mmOAjVcnsubksPqm546451T0gP406TNvs \
    --feature_group_name ohlc_feature_gropu \
    --feature_group_version 2 \
    --csv_file ./ohlc_data.csv
```


