"""
This file has been created to store all the misc variables currently being used due to buttons on the front end side .
The plan is to eliminate them in the future.

"""

master_comapnies = ["amazon", "american express ", "boeing", "johnson and johnson", "eli lily",
                             "meta" "tesla", "netflix", "P&G", "pfizer"]#"amazons", "american expresses", "boeings", "johnson and johnsons", "eli lilys", "metas", "teslas", "netflixes", "p&gs", "pfizers"]#["Amazons", "American Expresses", "Boeings", "Johnson and Johnsons", "Eli Lilys", "Metas", "Teslas", "Netflixes", "P&Gs", "Pfizers"]



company_name_to_code = {
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Netflix": "NFLX",
    "Google": "GOOG",
    "Meta" : "META",
    "American Express":"AXP",
    "Boeing":"BA",
    "Eli Lily":"LLY",
    "Pfizer":"PFE",
    "P&G":"PG",
    "Johnson and Johnson":"JNJ"
}

# Data to simulate available reports based on company and year
available_reports = {
    "AMZN": {
        "2022": ["10-K", "10-Q"],
        "2023": ["10-K", "10-Q"],
        "2024": ["10-Q"],  # 10-K not available for 2024
    },
    "TSLA": {
        "2022": ["10-K", "10-Q"],
        "2023": ["10-K", "10-Q"],
        "2024": ["10-Q"],
    },
    "NFLX": {
        "2022": ["10-K", "10-Q"],
        "2023": ["10-K", "10-Q"],
        "2024": ["10-Q"],
    },
    "GOOG": {
        "2022": ["10-K", "10-Q"],
        "2023": ["10-K", "10-Q"],
        "2024": ["10-Q"],
    },
    "META": {
        "2022": ["10-K", "10-Q"],
        "2023": ["10-K", "10-Q"],
        "2024": ["10-Q"]},

    "AXP": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]

    },
        "BA": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]},
        "LLY": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]},
"PFE": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]},

"PG": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]},

"JNJ": {
            "2022": ["10-K", "10-Q"],
            "2023": ["10-K", "10-Q"],
            "2024": ["10-Q"]},


}

