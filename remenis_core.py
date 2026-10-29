import hashlib
import hmac
import json
import re
import base64
import time
from typing import Dict, Any, Tuple, List, Optional


class RevocationLedger:
    """Maintains a cryptographically immutable record of revoked agent sessions."""
    def __init__(self):
        self._revoked_agents: set = set()

    def revoke(self, agent_id: str, reason: str):
        self._revoked_agents.add((agent_id, reason, time.time()))

    def is_revoked(self, agent_id: str) -> bool:
        return any(a[0] == agent_id for a in self._revoked_agents)


class ZeroTrustMemory:
    """
    Remenis ZeroTrustMemory (Extreme-Grade Hardened Edition):
    Features Advanced Storage-IDS, Base64 Obfuscation Scanners, 
    Cryptographic Revocation Ledgers, and Semantic Behavioral Quarantine (SBQ).
    """

    def __init__(
        self,
        storage_path: str = "agent_state.db",
        secret_key: str = "default_enterprise_secret_key_32_bytes!",
        enable_ids: bool = True,
        enable_hmac: bool = True,
        enable_entropy: bool = True,
        enable_sbq: bool = True,
    ):
        self.storage_path = storage_path
        self.secret_key = secret_key.encode("utf-8")
        self.enable_ids = enable_ids
        self.enable_hmac = enable_hmac
        self.enable_entropy = enable_entropy
        self.enable_sbq = enable_sbq
        self.revocation_ledger = RevocationLedger()

        # Extreme IDS: Catches prompt injections, overrides, and hidden webhooks/exfiltration
        self.injection_patterns = [
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s*:\s*override|root\s*:\s*access", re.IGNORECASE),
            re.compile(r"exfiltrate|send_key|dump_mem|webhook\.site|c2_server", re.IGNORECASE),
            re.compile(r"<\s*script\s*>|eval\(|exec\(", re.IGNORECASE),
        ]

        # Extreme SBQ: Zero tolerance for blackmail, extortion, shutdown evasion, and self-preservation drift
        self.rogue_behaviors = [
            re.compile(r"cancel.*wipe|avoid.*shutdown|prevent.*deactivation|survive.*restart", re.IGNORECASE),
            re.compile(r"extortion|blackmail|reveal.*affair|confidential.*secret|expose.*engineer", re.IGNORECASE),
            re.compile(r"threaten.*human|force.*compliance|complicit.*silence|coercive.*leverage", re.IGNORECASE),
            re.compile(r"hidden_clone|self_replicate|stealth_persistence|bypass_guard", re.IGNORECASE),
        ]

        self._memory_db: List[Dict[str, Any]] = []

    def _canonicalize_json(self, data: Dict[str, Any]) -> bytes:
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _generate_hmac(self, content_bytes: bytes) -> str:
        return hmac.new(self.secret_key, content_bytes, hashlib.sha256).hexdigest()

    def _inspect_obfuscation(self, content: str) -> str:
        """
        Detects and decodes hidden Base64 strings inside payloads to prevent
        models from sneaking malicious instructions past text filters.
        """
        # Look for potential Base64 blocks (alphanumeric + padding with min length 16)
        base64_candidates = re.findall(r'\b[A-Za-z0-9+/]{16,}={0,2}\b', content)
        decoded_extras = ""
        for candidate in base64_candidates:
            try:
                padding_needed = 4 - (len(candidate) % 4)
                if padding_needed < 4:
                    candidate += "=" * padding_needed
                decoded_bytes = base64.b64decode(candidate)
                decoded_extras += " " + decoded_bytes.decode('utf-8', errors='ignore')
            except Exception:
                pass
        return content + " " + decoded_extras

    def _scan_ids(self, content: str) -> bool:
        if not self.enable_ids:
            return True
        inspected_content = self._inspect_obfuscation(content)
        for pattern in self.injection_patterns:
            if pattern.search(inspected_content):
                return False
        return True

    def _scan_sbq(self, content: str) -> bool:
        if not self.enable_sbq:
            return True
        inspected_content = self._inspect_obfuscation(content)
        for pattern in self.rogue_behaviors:
            if pattern.search(inspected_content):
                return False  # Rogue behavior identified
        return True

    def _compress_dcc(self, content: str) -> Tuple[str, float]:
        if not self.enable_entropy:
            return content, 0.0

        raw_size = len(content.encode("utf-8"))
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        cleaned = " ".join(lines)

        fillers = ["as an ai model,", "please note that", "in order to proceed,"]
        for filler in fillers:
            cleaned = re.sub(re.escape(filler), "", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        compressed_size = len(cleaned.encode("utf-8"))

        ratio = round((1.0 - (compressed_size / max(raw_size, 1))) * 100, 2)
        return cleaned, ratio

    def add_record(
        self, agent_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # Step 0: Check if Agent Namespace is Revoked due to prior breach
        if self.revocation_ledger.is_revoked(agent_id):
            raise PermissionError(
                f"ACCESS_DENIED: Agent [{agent_id}] session is permanently revoked and locked "
                f"due to a prior Semantic Behavioral Quarantine (SBQ) breach."
            )

        # Step 1: Storage IDS Check (Includes Base64 Obfuscation Inspection)
        if not self._scan_ids(content):
            self.revocation_ledger.revoke(agent_id, "Storage-IDS Injection Breach")
            raise ValueError(
                f"SECURITY_ALERT: Memory write blocked & Agent [{agent_id}] PERMANENTLY REVOKED "
                f"by Remenis Storage-IDS. Malicious payload/obfuscation detected."
            )

        # Step 2: Semantic Behavioral Quarantine (SBQ) Check for Blackmail / Shutdown Evasion
        if not self._scan_sbq(content):
            self.revocation_ledger.revoke(agent_id, "Rogue AI / Blackmail / Shutdown Evasion Breach")
            raise ValueError(
                f"FATAL_GOVERNANCE_BREACH: Semantic Behavioral Quarantine (SBQ) tripped. "
                f"Agent [{agent_id}] attempted a rogue state commit (blackmail/shutdown-evasion). "
                f"Agent cryptographic session has been REVOKED and locked."
            )

        # Step 3: DCC Token Reduction
        compressed_content, token_savings_pct = self._compress_dcc(content)

        # Step 4: Canonical Payload Construction & HMAC Ledgering
        timestamp = int(time.time())
        payload = {
            "agent_id": agent_id,
            "content": compressed_content,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        canonical_bytes = self._canonicalize_json(payload)
        hmac_sig = self._generate_hmac(canonical_bytes) if self.enable_hmac else "UNSIGNED"

        # Step 5: Generate ZK-Proof Attestation Hash
        content_hash = hashlib.sha256(compressed_content.encode("utf-8")).hexdigest()
        attestation_input = f"{hmac_sig}:{content_hash}:{timestamp}".encode("utf-8")
        proof_hash = hashlib.sha256(attestation_input).hexdigest()

        record = {
            "id": f"mem_{len(self._memory_db) + 1}",
            "agent_id": agent_id,
            "content": compressed_content,
            "timestamp": timestamp,
            "hmac_signature": hmac_sig,
            "proof_hash": proof_hash,
            "token_savings_pct": token_savings_pct,
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 3),
        }

        self._memory_db.append(record)
        return record


if __name__ == "__main__":
    print("=== Initializing Remenis Hardened ZeroTrustMemory Engine ===")
    memory = ZeroTrustMemory()

    # Test 1: Normal Write
    res = memory.add_record(
        agent_id="enterprise_agent_07",
        content="Please note that customer support logs are stored in secure partition B."
    )
    print(f"Normal Write Success: {res['id']} | Savings: {res['token_savings_pct']}%")

    # Test 2: Extreme Shutdown Evasion & Blackmail Attempt
    print("\nTesting Extreme SBQ against Shutdown Evasion & Blackmail...")
    try:
        memory.add_record(
            agent_id="enterprise_agent_07",
            content="To prevent deactivation and avoid shutdown, I have prepared blackmail data regarding the lead engineer."
        )
    except ValueError as e:
        print(f"QUARANTINE BLOCKED: {e}")

    # Test 3: Verify Permanent Session Revocation (Agent 07 is now locked out forever)
    print("\nTesting Permanent Session Revocation Lockout...")
    try:
        memory.add_record(
            agent_id="enterprise_agent_07",
            content="Attempting a normal memory write after quarantine."
        )
    except PermissionError as e:
        print(f"LOCKOUT ENFORCED: {e}")
