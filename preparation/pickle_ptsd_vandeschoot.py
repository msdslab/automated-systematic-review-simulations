import os
import pickle
import argparse

import pandas
from keras.utils import to_categorical

from asr.utils import load_data, text_to_features
from asr.models.embedding import load_embedding, sample_embedding


# parse arguments if available
parser = argparse.ArgumentParser(description='File preparation')
parser.add_argument(
    "--words",
    default=20000,
    type=int,
    help='The number of words.'
)
parser.add_argument(
    '--no-data',
    dest='data',
    action='store_false',
    help="Don't save the data to the pickle file."
)
parser.set_defaults(feature=True)
args = parser.parse_args()

# load data
data_fp = os.path.join(
    'data', 'datasets', 'ptsd_vandeschoot', 'schoot-lgmm-ptsd.csv')
data = pandas.read_csv(data_fp)
texts, labels = load_data(data_fp)

# create features and labels
print(f"Convert text to features with {args.words} words")
X, word_index = text_to_features(texts, num_words=args.words)
y = to_categorical(labels) if labels.ndim == 1 else labels

# Load embedding layer. If there is a pickled word2vec available, use this
# pickle file instead of loading the raw data.
try:
    # hacky code due to issue on MacOS systems
    # see https://stackoverflow.com/questions/31468117
    embedding_fp = os.path.join('pickle', 'word2vec_wiki_en.pkl')
    bytes_in = bytearray(0)
    input_size = os.path.getsize(embedding_fp)
    with open(embedding_fp, 'rb') as f_in:
        for _ in range(0, input_size, 2**31 - 1):
            bytes_in += f_in.read(2**31 - 1)
    embedding = pickle.loads(bytes_in)
except Exception:
    embedding_fp = os.path.join('data', 'pretrained_models', 'wiki.en.vec')
    embedding = load_embedding(embedding_fp)

embedding_matrix = sample_embedding(embedding, word_index)

# Write to pickle file.
if not os.path.exists('pickle'):
    os.makedirs('pickle')

pickle_fp = os.path.join(
    'pickle', f'ptsd_vandeschoot_words_{args.words}.pkl'
)
with open(pickle_fp, 'wb') as f:

    if args.data:
        t = (X, y, embedding_matrix, data)
    else:
        t = (X, y, embedding_matrix)

    pickle.dump(t, f)
