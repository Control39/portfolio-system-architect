"""
Тесты для бизнес-логики System Proof.

Test Coverage:
- Proof creation and step management
- Verification and accuracy thresholds
- Proof collection operations
- Search and filtering
- Edge cases and validation
"""

import pytest

from apps.system_proof.proof_schema import ProofMetadata, SystemProof
from apps.system_proof.src.core import ProofCollection


class TestProofCreation:
    """Тесты создания и управления доказательствами."""

    def test_create_proof_with_required_fields(self):
        """Тест создания доказательства с обязательными полями."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=3,
        )

        proof = SystemProof(
            id="proof-001",
            chain_id="chain-001",
            metadata=metadata,
        )

        assert proof.id == "proof-001"
        assert proof.chain_id == "chain-001"
        assert len(proof.steps) == 0
        assert proof.verification_accuracy == 0.0

    def test_add_trace_step(self):
        """Тест добавления шага цепочки рассуждений."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=3,
        )

        proof = SystemProof(
            id="proof-001",
            chain_id="chain-001",
            metadata=metadata,
        )

        proof.add_step(
            input_text="What is FastAPI?",
            output_text="FastAPI is a modern web framework for Python.",
            step_metadata={"source": "documentation"},
        )

        assert len(proof.steps) == 1
        assert proof.steps[0].input == "What is FastAPI?"
        assert proof.steps[0].output == "FastAPI is a modern web framework for Python."
        assert proof.steps[0].metadata["source"] == "documentation"

    def test_add_multiple_steps(self):
        """Тест добавления нескольких шагов."""
        metadata = ProofMetadata(
            thought_architecture="Multi-Step-RAG",
            system_thinking_level=4,
        )

        proof = SystemProof(
            id="proof-002",
            chain_id="chain-002",
            metadata=metadata,
        )

        proof.add_step("Step 1 input", "Step 1 output")
        proof.add_step("Step 2 input", "Step 2 output")
        proof.add_step("Step 3 input", "Step 3 output")

        assert len(proof.steps) == 3
        assert proof.steps[2].input == "Step 3 input"

    def test_proof_with_auto_generated_id(self):
        """Тест доказательства с автогенерацией ID."""
        metadata = ProofMetadata(
            thought_architecture="Simple-CoT",
            system_thinking_level=2,
        )

        proof = SystemProof(
            chain_id="chain-003",
            metadata=metadata,
        )

        assert proof.id is not None
        assert len(proof.id) > 0


class TestVerification:
    """Тесты верификации доказательств."""

    def test_verify_above_threshold(self):
        """Тест верификации с точностью выше порога."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=4,
        )

        proof = SystemProof(
            id="proof-001",
            chain_id="chain-001",
            metadata=metadata,
            verification_accuracy=0.95,
        )

        result = proof.verify(threshold=0.9)

        assert result is True
        assert proof.metadata.verified is True

    def test_verify_below_threshold(self):
        """Тест верификации с точностью ниже порога."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=3,
        )

        proof = SystemProof(
            id="proof-002",
            chain_id="chain-002",
            metadata=metadata,
            verification_accuracy=0.85,
        )

        result = proof.verify(threshold=0.9)

        assert result is False
        assert proof.metadata.verified is False

    def test_verify_at_threshold(self):
        """Тест верификации точно на пороге."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=3,
        )

        proof = SystemProof(
            id="proof-003",
            chain_id="chain-003",
            metadata=metadata,
            verification_accuracy=0.9,
        )

        result = proof.verify(threshold=0.9)

        assert result is True
        assert proof.metadata.verified is True

    def test_verify_custom_threshold(self):
        """Тест верификации с кастомным порогом."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=3,
        )

        proof = SystemProof(
            id="proof-004",
            chain_id="chain-004",
            metadata=metadata,
            verification_accuracy=0.85,
        )

        result = proof.verify(threshold=0.8)

        assert result is True
        assert proof.metadata.verified is True


class TestProofToDict:
    """Тесты сериализации доказательств."""

    def test_to_dict_structure(self):
        """Тест структуры словаря доказательства."""
        metadata = ProofMetadata(
            thought_architecture="RAG-CoT",
            system_thinking_level=4,
            source_link="https://github.com/test/repo",
        )

        proof = SystemProof(
            id="proof-001",
            chain_id="chain-001",
            metadata=metadata,
            verification_accuracy=0.92,
        )
        proof.add_step("input1", "output1")
        proof.add_step("input2", "output2")

        proof.verify()
        result = proof.to_dict()

        assert result["id"] == "proof-001"
        assert result["chain_id"] == "chain-001"
        assert len(result["steps"]) == 2
        assert result["metadata"]["thought_architecture"] == "RAG-CoT"
        assert result["metadata"]["system_thinking_level"] == 4
        assert result["metadata"]["source_link"] == "https://github.com/test/repo"
        assert result["verification_accuracy"] == 0.92

    def test_to_dict_timestamp_format(self):
        """Тест формата timestamp в словаре."""
        metadata = ProofMetadata(
            thought_architecture="Simple-CoT",
            system_thinking_level=2,
        )

        proof = SystemProof(
            chain_id="chain-002",
            metadata=metadata,
        )

        result = proof.to_dict()

        assert "timestamp" in result["metadata"]
        assert isinstance(result["metadata"]["timestamp"], str)


class TestProofCollection:
    """Тесты коллекции доказательств."""

    @pytest.fixture
    def collection(self):
        """Создать пустую коллекцию."""
        return ProofCollection()

    @pytest.fixture
    def collection_with_data(self):
        """Создать коллекцию с тестовыми данными."""
        collection = ProofCollection()

        proofs = [
            SystemProof(
                id="proof-1",
                chain_id="chain-A",
                metadata=ProofMetadata(
                    thought_architecture="RAG-CoT",
                    system_thinking_level=4,
                ),
                verification_accuracy=0.95,
            ),
            SystemProof(
                id="proof-2",
                chain_id="chain-A",
                metadata=ProofMetadata(
                    thought_architecture="Multi-Step-RAG",
                    system_thinking_level=3,
                ),
                verification_accuracy=0.88,
            ),
            SystemProof(
                id="proof-3",
                chain_id="chain-B",
                metadata=ProofMetadata(
                    thought_architecture="RAG-CoT",
                    system_thinking_level=5,
                ),
                verification_accuracy=0.92,
            ),
        ]

        for proof in proofs:
            collection.add_proof(proof)

        return collection

    def test_add_proof(self, collection):
        """Тест добавления доказательства."""
        proof = SystemProof(
            id="proof-001",
            chain_id="chain-001",
            metadata=ProofMetadata(
                thought_architecture="Simple-CoT",
                system_thinking_level=2,
            ),
        )

        result_id = collection.add_proof(proof)

        assert result_id == "proof-001"
        assert collection.count == 1

    def test_get_proof(self, collection_with_data):
        """Тест получения доказательства по ID."""
        proof = collection_with_data.get_proof("proof-1")

        assert proof is not None
        assert proof.id == "proof-1"
        assert proof.chain_id == "chain-A"

    def test_get_nonexistent_proof(self, collection):
        """Тест получения несуществующего доказательства."""
        proof = collection.get_proof("nonexistent")
        assert proof is None

    def test_delete_proof(self, collection_with_data):
        """Тест удаления доказательства."""
        result = collection_with_data.delete_proof("proof-1")

        assert result is True
        assert collection_with_data.count == 2
        assert collection_with_data.get_proof("proof-1") is None

    def test_delete_nonexistent_proof(self, collection):
        """Тест удаления несуществующего доказательства."""
        result = collection.delete_proof("nonexistent")
        assert result is False

    def test_list_proofs(self, collection_with_data):
        """Тест перечисления всех доказательств."""
        proofs = collection_with_data.list_proofs()

        assert len(proofs) == 3
        proof_ids = {p.id for p in proofs}
        assert "proof-1" in proof_ids
        assert "proof-2" in proof_ids
        assert "proof-3" in proof_ids

    def test_find_by_chain_id(self, collection_with_data):
        """Тест поиска по chain_id."""
        proofs = collection_with_data.find_by_chain_id("chain-A")

        assert len(proofs) == 2
        for proof in proofs:
            assert proof.chain_id == "chain-A"

    def test_find_by_architecture(self, collection_with_data):
        """Тест поиска по архитектуре."""
        proofs = collection_with_data.find_by_architecture("RAG-CoT")

        assert len(proofs) == 2
        for proof in proofs:
            assert proof.metadata.thought_architecture == "RAG-CoT"

    def test_find_verified(self, collection_with_data):
        """Тест поиска верифицированных доказательств."""
        proofs = collection_with_data.find_verified(threshold=0.9)

        assert len(proofs) == 2
        for proof in proofs:
            assert proof.verification_accuracy >= 0.9

    def test_clear_collection(self, collection_with_data):
        """Тест очистки коллекции."""
        assert collection_with_data.count == 3

        collection_with_data.clear()

        assert collection_with_data.count == 0
        assert len(collection_with_data.list_proofs()) == 0


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_empty_steps_proof(self):
        """Тест доказательства без шагов."""
        proof = SystemProof(
            id="proof-empty",
            chain_id="chain-empty",
            metadata=ProofMetadata(
                thought_architecture="Empty-CoT",
                system_thinking_level=1,
            ),
        )

        assert len(proof.steps) == 0
        assert proof.to_dict()["steps"] == []

    def test_proof_with_empty_metadata(self):
        """Тест доказательства с пустыми метаданными шага."""
        proof = SystemProof(
            id="proof-meta",
            chain_id="chain-meta",
            metadata=ProofMetadata(
                thought_architecture="Test",
                system_thinking_level=2,
            ),
        )

        proof.add_step("input", "output", None)

        assert len(proof.steps) == 1
        assert proof.steps[0].metadata == {}

    def test_thinking_level_bounds(self):
        """Тест границ уровня системного мышления."""
        # Минимальное значение
        metadata_low = ProofMetadata(
            thought_architecture="Test",
            system_thinking_level=1,
        )
        assert metadata_low.system_thinking_level == 1

        # Максимальное значение
        metadata_high = ProofMetadata(
            thought_architecture="Test",
            system_thinking_level=5,
        )
        assert metadata_high.system_thinking_level == 5

    def test_accuracy_bounds(self):
        """Тест границ точности верификации."""
        # Минимальная точность
        proof_low = SystemProof(
            chain_id="chain-low",
            metadata=ProofMetadata(
                thought_architecture="Test",
                system_thinking_level=2,
            ),
            verification_accuracy=0.0,
        )
        assert proof_low.verification_accuracy == 0.0

        # Максимальная точность
        proof_high = SystemProof(
            chain_id="chain-high",
            metadata=ProofMetadata(
                thought_architecture="Test",
                system_thinking_level=2,
            ),
            verification_accuracy=1.0,
        )
        assert proof_high.verification_accuracy == 1.0

    def test_collection_with_single_proof(self):
        """Тест коллекции с одним доказательством."""
        collection = ProofCollection()
        proof = SystemProof(
            id="single",
            chain_id="single-chain",
            metadata=ProofMetadata(
                thought_architecture="Test",
                system_thinking_level=2,
            ),
        )

        collection.add_proof(proof)

        assert collection.count == 1
        assert len(collection.list_proofs()) == 1
        assert len(collection.find_by_chain_id("single-chain")) == 1
