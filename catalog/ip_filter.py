"""
IP Non-Infringement Scanner & Legal Defense Matrix

Automated trademark non-infringement scanner and IP defense matrix designed to protect
e-commerce catalog, generative AI prompts, and marketing content from infringing
Rockstar Games / Take-Two Interactive trademarks, while validating and approving
lawful 1980s/1990s Miami Vice City retro aesthetics, synthwave, and public domain tropes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class IPViolation:
    """Represents a detected trademark or proprietary IP violation."""
    term: str
    matched_pattern: str
    category: str
    context: str
    suggested_replacement: Optional[str] = None


@dataclass
class IPScanResult:
    """Structured result of an IP scan operation."""
    is_clean: bool
    violations: List[IPViolation] = field(default_factory=list)
    flagged_terms: List[str] = field(default_factory=list)
    sanitized_text: str = ""
    safe_suggestions: Dict[str, str] = field(default_factory=dict)
    checked_fields_count: int = 1


class IPFilter:
    """Automated trademark scanner and legal defense filter for GTA 6 inspired assets."""

    # Categorized proprietary marks owned by Rockstar Games / Take-Two Interactive
    TRADEMARK_CATEGORIES: Dict[str, List[str]] = {
        "company_publisher": [
            "rockstar",
            "rockstar games",
            "rockstar north",
            "take-two",
            "take two",
            "take-two interactive",
            "take two interactive",
            "r*",
        ],
        "game_titles": [
            "grand theft auto",
            "gta",
            "gta 6",
            "gta6",
            "gta vi",
            "gta_vi",
            "gta-vi",
            "gta 5",
            "gta5",
            "gta v",
            "gta_v",
            "gta 4",
            "gta iv",
            "gta iii",
            "gta vice city",
            "vice city stories",
            "san andreas",
            "liberty city stories",
        ],
        "game_characters": [
            "lucia",
            "jason",
            "tommy vercetti",
            "vercetti",
            "lance vance",
            "ricardo diaz",
            "sonny forelli",
            "ken rosenberg",
            "phil cassidy",
            "victor vance",
            "carl johnson",
            "franklin clinton",
            "michael de santa",
            "trevor philips",
            "niko bellic",
        ],
        "in_game_fictional_brands": [
            "ammu-nation",
            "ammunation",
            "sprunk",
            "ecola",
            "e-cola",
            "love fist",
            "weazel news",
            "cluckin bell",
            "cluckin' bell",
            "burger shot",
            "pisswasser",
            "pißwasser",
            "redwood cigarettes",
            "bawsaq",
            "flyus",
            "lifeinvader",
            "whiz wireless",
        ],
        "in_game_fictional_vehicles": [
            "grotti",
            "pegassi",
            "pfister",
            "declasse",
            "maibatsu",
            "dewbauchee",
            "benefactor",
        ],
        "proprietary_locations": [
            "leonida",
            "los santos",
            "san fierro",
            "las venturas",
            "liberty city",
            "starfish island",
            "prawn island",
            "escobar international airport",
        ],
    }

    # Safe legal replacement mappings to lawful 80s/90s Miami aesthetic tropes
    SAFE_REPLACEMENT_MAP: Dict[str, str] = {
        "grand theft auto": "Retro Miami Outrun",
        "gta 6": "80s Miami Synthwave",
        "gta6": "80s Miami Synthwave",
        "gta vi": "80s Miami Synthwave",
        "gta_vi": "80s Miami Synthwave",
        "gta-vi": "80s Miami Synthwave",
        "gta 5": "Retro West Coast Outrun",
        "gta5": "Retro West Coast Outrun",
        "gta v": "Retro West Coast Outrun",
        "gta": "Retro Vice Coast",
        "rockstar games": "Retro Studio",
        "rockstar north": "Retro Studio",
        "rockstar": "Retro Icon",
        "take-two interactive": "Creative Syndicate",
        "take two interactive": "Creative Syndicate",
        "take-two": "Creative Syndicate",
        "take two": "Creative Syndicate",
        "r*": "Retro Star",
        "lucia and jason": "retro miami crime duo",
        "lucia & jason": "retro miami crime duo",
        "lucia": "The Flamingo Driver",
        "jason": "The Vice Courier",
        "tommy vercetti": "The Hawaiian Shirt Don",
        "vercetti": "The Don",
        "lance vance": "The Pastel Pilot",
        "ricardo diaz": "The Kingpin",
        "sonny forelli": "The Syndicate Boss",
        "ammu-nation": "Ocean Drive Armory",
        "ammunation": "Ocean Drive Armory",
        "sprunk": "Vice Rush Soda",
        "ecola": "Tropic Cola",
        "e-cola": "Tropic Cola",
        "love fist": "Neon Fist Band",
        "weazel news": "Sunstate News '86",
        "cluckin bell": "Crispy Bird Diner",
        "cluckin' bell": "Crispy Bird Diner",
        "burger shot": "Neon Burger Bar",
        "leonida": "Sunstate Florida",
        "los santos": "Pacific Coast Metro",
        "san andreas": "Golden State",
        "starfish island": "Pelican Bay Cay",
        "prawn island": "Biscayne Isle",
        "grotti": "1984 Italian Wedge",
        "pegassi": "Retro Wedge Coupe",
        "pfister": "Stuttgart Classic",
    }

    # Approved aesthetic keywords establishing lawful retro-futurism inspiration
    LAWFUL_AESTHETIC_KEYWORDS: Set[str] = {
        "80s", "90s", "eighties", "nineties", "1980s", "1986", "1984",
        "vice", "vice coast", "vice city", "miami", "biscayne", "ocean drive",
        "south beach", "florida", "sunstate", "tropical", "palm", "flamingos",
        "synthwave", "retrowave", "outrun", "vaporwave", "neon", "cyberpunk",
        "art deco", "pastel", "retro-futurism", "holographic", "terrazzo",
        "camp collar", "corduroy", "aviator", "sunset", "golden hour",
    }

    def __init__(self, extra_banned_terms: Optional[List[str]] = None) -> None:
        self.compiled_rules: List[Tuple[re.Pattern, str, str]] = []
        self._build_regex_rules(extra_banned_terms or [])

    def _build_regex_rules(self, extra_banned_terms: List[str]) -> None:
        """Compile optimized regex rules with word boundary checks."""
        # Compile all categorized terms
        for category, terms in self.TRADEMARK_CATEGORIES.items():
            for term in terms:
                pattern = self._term_to_regex(term)
                self.compiled_rules.append((pattern, term, category))

        # Add custom extra banned terms
        for term in extra_banned_terms:
            cleaned = term.strip().lower()
            if cleaned:
                pattern = self._term_to_regex(cleaned)
                self.compiled_rules.append((pattern, cleaned, "custom_banned"))

        # Sort rules so longer phrases match before shorter substrings
        self.compiled_rules.sort(key=lambda rule: len(rule[1]), reverse=True)

    @staticmethod
    def _term_to_regex(term: str) -> re.Pattern:
        """Construct a robust word-boundary regex pattern handling spaces and punctuation."""
        if term == "r*":
            return re.compile(r"(?i)\br\*(?!\w)")
        elif term == "gta":
            return re.compile(r"(?i)(?:\bgta\b|\bg\.t\.a\.(?!\w))")

        parts = [re.escape(p) for p in re.split(r"[ \-_]+", term) if p]
        if len(parts) > 1:
            joined = r"[\s\-_]+".join(parts)
            return re.compile(rf"(?i)(?:\b|(?<=_)){joined}(?:\b|(?=_))")
        else:
            return re.compile(rf"(?i)\b{parts[0]}\b")

    def scan_text(self, text: str) -> IPScanResult:
        """
        Scan a text string for any protected trademark or IP infringement.
        Returns IPScanResult detailing violations and safe suggestions.
        """
        if not text:
            return IPScanResult(is_clean=True, sanitized_text=text)

        violations: List[IPViolation] = []
        flagged_terms: List[str] = []
        suggestions: Dict[str, str] = {}
        seen_matches: Set[str] = set()

        for pattern, term, category in self.compiled_rules:
            for match in pattern.finditer(text):
                matched_str = match.group(0)
                norm_term = term.lower()
                if norm_term not in seen_matches:
                    seen_matches.add(norm_term)
                    # Extract surrounding context (30 chars)
                    start = max(0, match.start() - 25)
                    end = min(len(text), match.end() + 25)
                    context_snippet = f"...{text[start:end]}..."

                    replacement = self.SAFE_REPLACEMENT_MAP.get(norm_term)
                    violations.append(
                        IPViolation(
                            term=term,
                            matched_pattern=matched_str,
                            category=category,
                            context=context_snippet,
                            suggested_replacement=replacement,
                        )
                    )
                    flagged_terms.append(term)
                    if replacement:
                        suggestions[term] = replacement

        is_clean = len(violations) == 0
        sanitized = self.sanitize_text(text) if not is_clean else text

        return IPScanResult(
            is_clean=is_clean,
            violations=violations,
            flagged_terms=flagged_terms,
            sanitized_text=sanitized,
            safe_suggestions=suggestions,
            checked_fields_count=1,
        )

    def sanitize_text(self, text: str) -> str:
        """
        Automatically replace banned trademarks with lawful retro Miami aesthetic homages.
        """
        if not text:
            return text

        result = text
        for pattern, term, _ in self.compiled_rules:
            replacement = self.SAFE_REPLACEMENT_MAP.get(term.lower(), "Retro Vice Aesthetic")
            result = pattern.sub(replacement, result)

        return result

    def scan_dict(self, data: Dict[str, Any], path_prefix: str = "") -> IPScanResult:
        """
        Recursively scan a dictionary for IP violations across all string values.
        """
        all_violations: List[IPViolation] = []
        all_flagged: List[str] = []
        all_suggestions: Dict[str, str] = {}
        fields_checked = 0

        for key, value in data.items():
            current_path = f"{path_prefix}.{key}" if path_prefix else key
            if isinstance(value, str):
                fields_checked += 1
                res = self.scan_text(value)
                if not res.is_clean:
                    for v in res.violations:
                        v.context = f"Field [{current_path}]: {v.context}"
                        all_violations.append(v)
                    all_flagged.extend(res.flagged_terms)
                    all_suggestions.update(res.safe_suggestions)
            elif isinstance(value, dict):
                sub_res = self.scan_dict(value, current_path)
                fields_checked += sub_res.checked_fields_count
                all_violations.extend(sub_res.violations)
                all_flagged.extend(sub_res.flagged_terms)
                all_suggestions.update(sub_res.safe_suggestions)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    item_path = f"{current_path}[{idx}]"
                    if isinstance(item, str):
                        fields_checked += 1
                        res = self.scan_text(item)
                        if not res.is_clean:
                            for v in res.violations:
                                v.context = f"Field [{item_path}]: {v.context}"
                                all_violations.append(v)
                            all_flagged.extend(res.flagged_terms)
                            all_suggestions.update(res.safe_suggestions)
                    elif isinstance(item, dict):
                        sub_res = self.scan_dict(item, item_path)
                        fields_checked += sub_res.checked_fields_count
                        all_violations.extend(sub_res.violations)
                        all_flagged.extend(sub_res.flagged_terms)
                        all_suggestions.update(sub_res.safe_suggestions)

        return IPScanResult(
            is_clean=len(all_violations) == 0,
            violations=all_violations,
            flagged_terms=list(set(all_flagged)),
            safe_suggestions=all_suggestions,
            checked_fields_count=fields_checked,
        )

    def scan_product(self, product: Dict[str, Any]) -> IPScanResult:
        """Scan a single product item dictionary for trademark compliance."""
        return self.scan_dict(product)

    def scan_catalog(self, catalog_data: Dict[str, Any] | List[Dict[str, Any]]) -> Tuple[bool, Dict[str, IPScanResult]]:
        """
        Scan an entire catalog (either a catalog dict with 'products' or a list of products).
        Returns (all_clean, results_per_product_id).
        """
        results: Dict[str, IPScanResult] = {}
        products: List[Dict[str, Any]] = []

        if isinstance(catalog_data, dict):
            # Check store-level fields first
            store_res = self.scan_dict({k: v for k, v in catalog_data.items() if k != "products"})
            results["store_metadata"] = store_res
            products = catalog_data.get("products", [])
        elif isinstance(catalog_data, list):
            products = catalog_data

        all_clean = True
        for product in products:
            p_id = product.get("id", product.get("sku", "unknown"))
            prod_res = self.scan_product(product)
            results[p_id] = prod_res
            if not prod_res.is_clean:
                all_clean = False

        if "store_metadata" in results and not results["store_metadata"].is_clean:
            all_clean = False

        return all_clean, results

    def verify_aesthetic_alignment(self, text: str) -> Dict[str, Any]:
        """
        Verify that the text positively incorporates lawful 1980s/1990s Vice City aesthetic tokens.
        """
        lowered = text.lower()
        matched_keywords = [kw for kw in self.LAWFUL_AESTHETIC_KEYWORDS if kw in lowered]
        score = len(matched_keywords)
        is_aligned = score >= 1

        return {
            "is_aligned": is_aligned,
            "alignment_score": score,
            "matched_keywords": matched_keywords,
            "recommendation": (
                "Sufficient retro-futuristic aesthetic markers detected."
                if is_aligned
                else "Consider infusing more 1980s Miami, synthwave, neon, or art deco descriptors."
            ),
        }


# Global default scanner instance
_default_filter = IPFilter()


def scan_text(text: str) -> IPScanResult:
    """Convenience functional interface to scan text."""
    return _default_filter.scan_text(text)


def sanitize_text(text: str) -> str:
    """Convenience functional interface to sanitize text."""
    return _default_filter.sanitize_text(text)


def scan_product(product: Dict[str, Any]) -> IPScanResult:
    """Convenience functional interface to scan a product dictionary."""
    return _default_filter.scan_product(product)


def scan_catalog(catalog: Dict[str, Any] | List[Dict[str, Any]]) -> Tuple[bool, Dict[str, IPScanResult]]:
    """Convenience functional interface to scan an entire catalog."""
    return _default_filter.scan_catalog(catalog)
