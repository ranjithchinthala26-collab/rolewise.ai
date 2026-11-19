# Machine Learning Fundamentals — starter study notes

These original starter notes are provided to make the demo usable. For the assignment submission, add the permitted course/book PDF selected from the assignment's Knowledge Base Resources to this directory and run the ingestion script. The uploaded book should be the primary source for your final evaluation corpus.

## Learning from data
A machine-learning system uses data to improve performance on a task. A typical workflow defines the task and success metric, collects and inspects data, prepares features, selects a model, trains it, evaluates it on data not used for fitting, and monitors it after deployment. A model that performs well on training data but poorly on unseen examples is overfitting. Underfitting occurs when the model is too simple or insufficiently trained to capture useful structure.

## Supervised learning
In supervised learning, each training example contains input features and a target label or value. Classification predicts a discrete class, while regression predicts a continuous value. The training objective is to learn a mapping that generalizes to new examples. Data leakage occurs when information unavailable at prediction time enters training or evaluation and can make metrics misleading.

## Model evaluation
Evaluation should match the task and the cost of errors. Accuracy is the fraction of correct predictions, but it can be misleading for imbalanced classes. Precision measures the fraction of predicted positives that are correct; recall measures the fraction of actual positives found. The F1 score is the harmonic mean of precision and recall. A confusion matrix makes false positives and false negatives visible. Keep a test set separate until model choices are complete; use validation data or cross-validation for model selection.

## Feature engineering and preprocessing
Preprocessing may include handling missing values, encoding categorical variables, scaling numeric features, and detecting inconsistent records. Fit transformations on training data only, then apply the learned transformations to validation and test data. Pipelines help keep preprocessing and model fitting consistent and reduce leakage.

## Embeddings and semantic search
An embedding maps text or another object to a numeric vector so that semantic similarity can be compared geometrically. Text is split into chunks that preserve enough surrounding context to be meaningful. A vector index retrieves chunks whose embeddings are close to a query embedding. Chunk size, overlap, metadata filters, and the number of retrieved chunks affect relevance and latency.

## Retrieval-augmented generation
RAG combines retrieval with generation. First, documents are loaded, cleaned, split into chunks, embedded, and stored. At query time, the application forms a query, retrieves relevant chunks, and places those chunks in the model context. The generator should answer using retrieved evidence and avoid unsupported claims. Useful systems retain source metadata so outputs can be traced to the material that informed them. Retrieval quality should be checked independently from answer quality.

## Responsible model use
A useful evaluation process checks factual correctness, consistency, robustness, latency, and failure behavior. Human review is important for high-impact decisions. A screening assistant should support structured assessment rather than make an opaque hiring decision. It should minimize personal data, explain its limitations, and allow a reviewer to inspect questions, answers, and evidence.
