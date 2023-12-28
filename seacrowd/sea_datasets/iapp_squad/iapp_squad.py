# coding=utf-8
import json

import datasets

from seacrowd.utils import schemas
from seacrowd.utils.configs import SEACrowdConfig
from seacrowd.utils.constants import Licenses, Tasks

_DATASETNAME = "iapp_squad"
_CITATION = """\
            @dataset
            {
              kobkrit_viriyayudhakorn_2021_4539916,
              author       = {Kobkrit Viriyayudhakorn and Charin Polpanumas},
              title        = {iapp_wiki_qa_squad},
              month        = feb,
              year         = 2021,
              publisher    = {Zenodo},
              version      = 1,
              doi          = {10.5281/zenodo.4539916},
              url          = {https://doi.org/10.5281/zenodo.4539916}
            }
            """

_DESCRIPTION = """
            `iapp_wiki_qa_squad` is an extractive question answering dataset from Thai Wikipedia articles.
            It is adapted from [the original iapp-wiki-qa-dataset](https://github.com/iapp-technology/iapp-wiki-qa-dataset)
            to [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) format, resulting in
            5761/742/739 questions from 1529/191/192 articles.
            """

_HOMEPAGE = "https://github.com/iapp-technology/iapp-wiki-qa-dataset"
_LICENSE = Licenses.MIT
_HF_URL = " https://huggingface.co/datasets/iapp_wiki_qa_squad"
_SUPPORTED_TASKS = [Tasks.QUESTION_ANSWERING]

_SOURCE_VERSION = "1.0.0"
_SEACROWD_VERSION = "0.0.0"

_IAPP = {
    "train": "https://raw.githubusercontent.com/iapp-technology/iapp-wiki-qa-dataset/main/squad_format/data/train.jsonl",
    "validation": "https://raw.githubusercontent.com/iapp-technology/iapp-wiki-qa-dataset/main/squad_format/data/valid.jsonl",
    "test": "https://raw.githubusercontent.com/iapp-technology/iapp-wiki-qa-dataset/main/squad_format/data/test.jsonl",
}


class IappWikiQaSquad(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIGS = [
        SEACrowdConfig(name="iapp_squad_source", version=datasets.Version(_SOURCE_VERSION), description=_DESCRIPTION, subset_id="iapp_squad", schema="source"),
        SEACrowdConfig(name="iapp_squad_seacrowd_qa", version=datasets.Version(_SOURCE_VERSION), description=_DESCRIPTION, subset_id="iapp_squad", schema="seacrowd"),
    ]

    def _info(self):
        if self.config.schema == "source":
            return datasets.DatasetInfo(
                # This is the description that will appear on the datasets page.
                description=_DESCRIPTION,
                # datasets.features.FeatureConnectors
                features=datasets.Features(
                    {
                        "question_id": datasets.Value("string"),
                        "article_id": datasets.Value("string"),
                        "title": datasets.Value("string"),
                        "context": datasets.Value("string"),
                        "question": datasets.Value("string"),
                        "answers": datasets.features.Sequence(
                            {
                                "text": datasets.Value("string"),
                                "answer_start": datasets.Value("int32"),
                                "answer_end": datasets.Value("int32"),
                            }
                        ),
                    }
                ),
                supervised_keys=None,
                homepage="https://github.com/iapp-technology/iapp-wiki-qa-dataset/",
                citation=_CITATION,
            )
        elif self.config.schema == "seacrowd":
            features = schemas.qa_features
            features["meta"] = {
                "answer_start": datasets.Value("int32"),
                "answer_end": datasets.Value("int32"),
            }
            return datasets.DatasetInfo(
                description=_DESCRIPTION,
                features=features,
                supervised_keys=None,
                homepage="https://github.com/iapp-technology/iapp-wiki-qa-dataset/",
                citation=_CITATION,
            )

    def _split_generators(self, dl_manager):
        file_paths = dl_manager.download_and_extract(_IAPP)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": file_paths["train"]},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"filepath": file_paths["validation"]},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": file_paths["test"]},
            ),
        ]

    def _generate_examples(self, filepath):
        """Yields examples."""
        with open(filepath, encoding="utf-8") as f:
            for id_, row in enumerate(f):
                data = json.loads(row)
                if self.config.schema == "source":
                    yield id_, {
                        "question_id": data["question_id"],
                        "article_id": data["article_id"],
                        "title": data["title"],
                        "context": data["context"],
                        "question": data["question"],
                        "answers": {
                            "text": data["answers"]["text"],
                            "answer_start": data["answers"]["answer_start"],
                            "answer_end": data["answers"]["answer_end"],
                        },
                    }
                elif self.config.schema == "seacrowd":
                    yield id_, {
                        "id": id_,
                        "question_id": data["question_id"],
                        "document_id": data["article_id"],
                        "question": data["question"],
                        "type": "abstractive",
                        "choices": [],
                        "context": data["context"],
                        "answer": data["answers"]["text"],
                        "meta": {"answer_start": data["answers"]["answer_start"][0], "answer_end": data["answers"]["answer_end"][0]},
                    }