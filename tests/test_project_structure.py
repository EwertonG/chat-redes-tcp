import unittest

import chat_tcp


class ProjectStructureTests(unittest.TestCase):
    """Confirma que o pacote principal pode ser carregado."""

    def test_package_exposes_version(self) -> None:
        self.assertEqual(chat_tcp.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()