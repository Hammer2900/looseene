import unittest
import os
import shutil
import time
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from looseene import (
    create_index,
    add_to_index,
    search_text,
    highlight_result,
    save_index,
    compact_index,
    get_index,
    ValidationError,
)


class TestLooseene(unittest.TestCase):
    def setUp(self):
        """Создает временную папку для тестов перед каждым тестом."""
        self.test_path = 'test_index_data'
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)
        create_index('test_idx', schema={'id': int, 'title': str, 'content': str}, path=self.test_path)

    def tearDown(self):
        """Удаляет временную папку после каждого теста."""
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)

    def test_01_add_and_search(self):
        """Тест на добавление и простой поиск."""
        add_to_index('test_idx', {'id': 1, 'title': 'Fox', 'content': 'The quick brown fox.'})
        add_to_index('test_idx', {'id': 2, 'title': 'Dog', 'content': 'A lazy dog.'})
        results = list(search_text('test_idx', 'fox'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)

    def test_02_persistence_and_flush(self):
        """Тест сохранения на диск и загрузки."""
        add_to_index('test_idx', {'id': 10, 'content': 'Data to be saved.'})
        save_index('test_idx')
        create_index('test_idx', schema={'id': int, 'content': str}, path=self.test_path)
        results = list(search_text('test_idx', 'saved'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 10)

    def test_03_delete_and_update(self):
        """Тест удаления и обновления."""
        add_to_index('test_idx', {'id': 20, 'content': 'This will be deleted.'})
        add_to_index('test_idx', {'id': 21, 'content': 'This will be updated.'})
        from looseene import delete_document, update_document

        delete_document('test_idx', 20)
        update_document('test_idx', {'id': 21, 'content': 'This is now fresh.'})
        deleted_results = list(search_text('test_idx', 'deleted'))
        self.assertEqual(len(deleted_results), 0)
        updated_results = list(search_text('test_idx', 'fresh'))
        self.assertEqual(len(updated_results), 1)
        self.assertEqual(updated_results[0]['id'], 21)

    def test_04_highlighting(self):
        """Тест подсветки результатов."""
        text = 'A search engine provides relevant search results.'
        add_to_index('test_idx', {'id': 30, 'content': text})
        query = 'relevant engine'
        doc = list(search_text('test_idx', query))[0]
        snippet = highlight_result(doc, 'content', query)
        expected = '...search <b>engine</b> provides <b>relevant</b> search results.'
        self.assertEqual(snippet, expected)

    def test_05_compaction(self):
        """Тест слияния сегментов."""
        add_to_index('test_idx', {'id': 40, 'content': 'Segment one'})
        save_index('test_idx')
        add_to_index('test_idx', {'id': 41, 'content': 'Segment two'})
        from looseene import delete_document

        delete_document('test_idx', 40)
        save_index('test_idx')
        idx = get_index('test_idx')
        self.assertEqual(len(idx.segments), 2, 'Should have 2 segments before compaction.')
        compact_index('test_idx')
        self.assertEqual(len(idx.segments), 1, 'Should have 1 segment after compaction.')
        results = list(search_text('test_idx', 'one'))
        self.assertEqual(len(results), 0)
        results = list(search_text('test_idx', 'two'))
        self.assertEqual(len(results), 1)

    def test_06_validation_error(self):
        """Тест валидации схемы."""
        with self.assertRaises(ValidationError, msg='Should raise on wrong ID type'):
            add_to_index('test_idx', {'id': 'wrong_id_type', 'content': '...'})

    def test_07_performance_load(self):
        """Нагрузочный тест на индексацию и поиск."""
        print('\n--- Running Performance Test ---')
        num_docs = 1000
        sentences = [
            'The quick brown fox jumps over the lazy dog',
            'Lorem ipsum dolor sit amet consectetur adipiscing elit',
            'Python is a high level programming language for general purpose programming',
        ]
        start_time = time.time()
        for i in range(num_docs):
            add_to_index('test_idx', {'id': 1000 + i, 'content': sentences[i % 3]})
        save_index('test_idx')
        indexing_time = time.time() - start_time
        print(f'Indexed {num_docs} docs in {indexing_time:.4f}s')
        query = 'brown fox'
        search_start_time = time.time()
        results = list(search_text('test_idx', query))
        search_time = time.time() - search_start_time
        print(f"Searched for '{query}' and found {len(results)} results in {search_time:.6f}s")
        self.assertGreater(len(results), 0)
        self.assertLess(search_time, 0.1, 'Search should be reasonably fast')


if __name__ == '__main__':
    unittest.main()
