import unittest
import holmes_extractor as holmes
from holmes_extractor.errors import *
import jsonpickle

nocoref_holmes_manager = holmes.Manager('en_core_web_lg', analyze_derivational_morphology=False,
                                        perform_coreference_resolution=False)
coref_holmes_manager = holmes.Manager(
    'en_core_web_lg', perform_coreference_resolution=True)
german_holmes_manager = holmes.Manager('de_core_news_md')


class ErrorsTest(unittest.TestCase):

    def test_overall_similarity_threshold_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_lg',
                           overall_similarity_threshold=1.2)

    def test_embedding_based_matching_on_root_node_where_no_embedding_based_matching(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_lg', overall_similarity_threshold=1.0,
                           embedding_based_matching_on_root_words=True)

    def test_model_does_not_support_embeddings(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='en_core_web_sm',
                           overall_similarity_threshold=0.85)

    def test_language_not_supported(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='fr_core_news_sm')

    def test_coreference_resolution_not_supported_error(self):
        with self.assertRaises(ValueError) as context:
            holmes.Manager(model='de_core_news_md',
                           perform_coreference_resolution=True)

    def test_coreference_resolution_not_supported_multiprocessing_manager_error(self):
        with self.assertRaises(ValueError) as context:
            holmes.MultiprocessingManager(model='de_core_news_md',
                                          perform_coreference_resolution=True)

    def test_search_phrase_contains_conjunction(self):
        with self.assertRaises(SearchPhraseContainsConjunctionError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "A dog and a lion chase a cat")

    def test_search_phrase_contains_negation(self):
        with self.assertRaises(SearchPhraseContainsNegationError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "A dog does not chase a cat")

    def test_search_phrase_contains_non_coreferring_pronoun(self):
        nocoref_holmes_manager.remove_all_search_phrases()
        nocoref_holmes_manager.register_search_phrase(
            "A cat has a dog chasing it")

    def test_search_phrase_contains_pronoun_coreference_switched_off(self):
        nocoref_holmes_manager.remove_all_search_phrases()
        nocoref_holmes_manager.register_search_phrase(
            "A cat has a dog chasing it")

    def test_search_phrase_contains_coreferring_pronoun(self):
        with self.assertRaises(SearchPhraseContainsCoreferringPronounError) as context:
            coref_holmes_manager.remove_all_search_phrases()
            coref_holmes_manager.register_search_phrase(
                "A cat has a dog chasing it")

    def test_search_phrase_contains_only_generic_pronoun(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("Somebody")

    def test_search_phrase_contains_only_interrogative_pronoun(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("Who")

    def test_search_phrase_contains_only_grammatical_word(self):
        with self.assertRaises(SearchPhraseWithoutMatchableWordsError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase("A")

    def test_search_phrase_contains_two_normal_clauses(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "The dog chased the cat. The cat chased the dog.")

    def test_search_phrase_contains_two_entity_clauses(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "An ENTITYPERSON. An ENTITYPERSON")

    def test_search_phrase_contains_one_normal_and_one_entity_clause(self):
        with self.assertRaises(SearchPhraseContainsMultipleClausesError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.register_search_phrase(
                "The dog chased the cat. An ENTITYPERSON")

    def test_duplicate_document_with_parse_and_register_document(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document("A", "A")
            nocoref_holmes_manager.parse_and_register_document("A", "A")

    def test_duplicate_document_with_register_parsed_document(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            holmes_doc = nocoref_holmes_manager.semantic_analyzer.parse("A")
            holmes_doc2 = nocoref_holmes_manager.semantic_analyzer.parse("B")
            nocoref_holmes_manager.register_parsed_document(holmes_doc, 'C')
            nocoref_holmes_manager.register_parsed_document(holmes_doc2, 'C')

    def test_duplicate_document_with_deserialize_and_register_document(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.parse_and_register_document("A", '')
            deserialized_doc = nocoref_holmes_manager.serialize_document('')
            nocoref_holmes_manager.deserialize_and_register_document(
                deserialized_doc, '')

    def test_duplicate_document_with_parse_and_register_documents_multiprocessing(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            m = holmes.MultiprocessingManager(
                'en_core_web_sm', number_of_workers=2)
            m.parse_and_register_documents({'A': "A"})
            m.parse_and_register_documents({'A': "A"})

    def test_duplicate_document_with_deserialize_and_register_document_multiprocessing(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            m_normal = holmes.Manager(
                'en_core_web_sm', perform_coreference_resolution=False)
            m_normal.remove_all_documents()
            m_normal.parse_and_register_document("A", '')
            deserialized_doc = m_normal.serialize_document('')
            m = holmes.MultiprocessingManager('en_core_web_sm',
                                              perform_coreference_resolution=False, number_of_workers=2)
            m.deserialize_and_register_documents({'A': deserialized_doc})
            m.deserialize_and_register_documents({'A': deserialized_doc})

    def test_serialization_not_supported_on_serialization(self):
        with self.assertRaises(SerializationNotSupportedError) as context:
            coref_holmes_manager.remove_all_documents()
            coref_holmes_manager.parse_and_register_document("A", '')
            deserialized_doc = coref_holmes_manager.serialize_document('')

    def test_serialization_not_supported_on_serialization_multiprocessing(self):
        with self.assertRaises(SerializationNotSupportedError) as context:
            m_normal = holmes.Manager(
                'en_core_web_sm', perform_coreference_resolution=False)
            m_normal.remove_all_documents()
            m_normal.parse_and_register_document("A", '')
            deserialized_doc = m_normal.serialize_document('')
            m = holmes.MultiprocessingManager(
                'en_core_web_sm', number_of_workers=2)
            m.deserialize_and_register_documents({'A': deserialized_doc})

    def test_serialization_not_supported_on_deserialization(self):
        with self.assertRaises(SerializationNotSupportedError) as context:
            nocoref_holmes_manager.remove_all_documents()
            coref_holmes_manager.remove_all_documents()
            coref_holmes_manager.deserialize_and_register_document("A", '')
            nocoref_holmes_manager.parse_and_register_document("A", '')
            deserialized_doc = nocoref_holmes_manager.serialize_document('')
            nocoref_holmes_manager.deserialize_and_register_document(
                deserialized_doc, '')

    def test_no_search_phrase_error(self):
        with self.assertRaises(NoSearchPhraseError) as context:
            nocoref_holmes_manager.remove_all_search_phrases()
            nocoref_holmes_manager.match_search_phrases_against("Try this")

    def test_no_document_error(self):
        with self.assertRaises(NoSearchedDocumentError) as context:
            nocoref_holmes_manager.remove_all_documents()
            nocoref_holmes_manager.match_documents_against("Try this")

    def test_wrong_model_deserialization_error_documents(self):
        with self.assertRaises(WrongModelDeserializationError) as context:
            nocoref_holmes_manager.remove_all_documents()
            doc = nocoref_holmes_manager.parse_and_register_document(
                "The cat was chased by the dog", 'pets')
            serialized_doc = nocoref_holmes_manager.serialize_document('pets')
            german_holmes_manager.deserialize_and_register_document(
                serialized_doc, 'pets')

    def test_wrong_version_deserialization_error_documents(self):
        with self.assertRaises(WrongVersionDeserializationError) as context:
            nocoref_holmes_manager.remove_all_documents()
            doc = nocoref_holmes_manager.parse_and_register_document(
                "The cat was chased by the dog", 'pets')
            serialized_doc = nocoref_holmes_manager.serialize_document('pets')
            document = jsonpickle.decode(serialized_doc)
            document._version = 1
            serialized_doc = jsonpickle.encode(document)
            nocoref_holmes_manager.deserialize_and_register_document(
                serialized_doc, 'pets2')

    def test_wrong_model_deserialization_error_supervised_models(self):
        with self.assertRaises(WrongModelDeserializationError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.parse_and_register_training_document("Katze", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = coref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_derivational_morphology_deserialization_error_supervised_models_true_false(self):
        with self.assertRaises(IncompatibleAnalyzeDerivationalMorphologyDeserializationError) \
                as context:
            sttb = nocoref_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("cat", 'animal', 't1')
            sttb.parse_and_register_training_document("mouse", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = coref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_derivational_morphology_deserialization_error_supervised_models_false_true(self):
        with self.assertRaises(IncompatibleAnalyzeDerivationalMorphologyDeserializationError) \
                as context:
            sttb = coref_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("cat", 'animal', 't1')
            sttb.parse_and_register_training_document("mouse", 'IT', 't2')
            sttb.prepare()
            stc = sttb.train(minimum_occurrences=0,
                             cv_threshold=0).classifier()
            serialized_supervised_topic_classifier_model = stc.serialize_model()
            stc2 = nocoref_holmes_manager.deserialize_supervised_topic_classifier(
                serialized_supervised_topic_classifier_model)

    def test_fewer_than_two_classifications_error(self):
        with self.assertRaises(FewerThanTwoClassificationsError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.prepare()

    def test_duplicate_document_with_train_supervised_model(self):
        with self.assertRaises(DuplicateDocumentError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis()
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')
            sttb.parse_and_register_training_document("Katze", 'Tiere', 't1')

    def test_no_phraselets_after_filtering_error(self):
        with self.assertRaises(NoPhraseletsAfterFilteringError) as context:
            sttb = german_holmes_manager.get_supervised_topic_training_basis(
                oneshot=False)
            sttb.parse_and_register_training_document(
                "Ein Hund jagt eine Katze", 'Tiere1', 't1')
            sttb.parse_and_register_training_document(
                "Ein Hund jagt eine Katze", 'Tiere2', 't2')
            sttb.prepare()
            sttb.train()

    def test_embedding_threshold_higher_than_relation_threshold_normal_manager(self):
        with self.assertRaises(EmbeddingThresholdGreaterThanRelationThresholdError) as context:
            m = holmes.Manager('en_core_web_sm')
            m.parse_and_register_document("a")
            coref_holmes_manager.topic_match_documents_returning_dictionaries_against("b",
                                                                                      maximum_number_of_single_word_matches_for_relation_matching=1,
                                                                                      maximum_number_of_single_word_matches_for_embedding_matching=2)

    def test_embedding_threshold_higher_than_relation_threshold_multiprocessing_manager(self):
        with self.assertRaises(EmbeddingThresholdGreaterThanRelationThresholdError) as context:
            m = holmes.MultiprocessingManager(
                'en_core_web_sm', number_of_workers=1)
            m.parse_and_register_documents({'': "a"})
            m.topic_match_documents_returning_dictionaries_against("b",
                                                                   maximum_number_of_single_word_matches_for_relation_matching=1,
                                                                   maximum_number_of_single_word_matches_for_embedding_matching=2)
