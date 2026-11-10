# Datasets

## 1. Dataset strategy

There is no single public dataset that can realistically represent the complete Personal Health Gateway.

Use a hybrid strategy:

1. public datasets for specific ML tasks;
2. synthetic healthcare records for application testing;
3. controlled sample documents for OCR/parsing;
4. generated time-series data for trend pipelines where real longitudinal datasets are unavailable.

## 2. Dataset categories

### Public / research datasets

Select datasets according to the specific research task and license.

Potential categories:

- vital-sign time series;
- diabetes/cardiovascular risk;
- medication/adherence research;
- clinical laboratory measurements;
- clinical text;
- medical-document structure.

### Synthetic data

Use synthetic data for:

- user accounts;
- personal profiles;
- vitals;
- lab results;
- medications;
- appointments;
- health events;
- consent records.

## 3. Dataset documentation

For each dataset record:

- source;
- license/terms;
- population;
- features;
- target;
- preprocessing;
- known bias;
- intended use;
- prohibited use;
- citation.

## 4. Dataset quality

Validate:

- schema;
- missing values;
- duplicates;
- invalid ranges;
- date consistency;
- class balance;
- leakage risk.

## 5. Source of truth

Application records must never be silently overwritten by an ML dataset. Training data is a separate concern from production user data.
