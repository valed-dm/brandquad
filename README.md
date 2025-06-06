# 🕷️ E-commerce Scraper (Pure Scrapy)  

A minimalistic, production-ready Scrapy spider for e-commerce product data extraction.  

<!-- Badge Definitions -->
[scrapy-badge]: https://img.shields.io/badge/Scrapy-2.11+-brightgreen
[scrapy-link]: https://scrapy.org/
[python-badge]: https://img.shields.io/badge/Python-3.12%2B-blue
[python-link]: https://www.python.org/
[license-badge]: https://img.shields.io/badge/License-MIT-yellow
[license-link]: LICENSE
[coverage-badge]: https://img.shields.io/badge/coverage-80%25-green
[ci-badge]: https://github.com/valed-dm/brandquas/actions/workflows/ci.yml/badge.svg
[ci-link]: https://github.com/valed-dm/brandquas/actions/workflows/ci.yml

<!-- Badges -->
[![Scrapy][scrapy-badge]][scrapy-link]
[![Python][python-badge]][python-link]
[![License][license-badge]][license-link]
![Coverage][coverage-badge]
[![CI][ci-badge]][ci-link]

## Features  
- **Pure Scrapy** (no external dependencies beyond `scrapy`)  
- Structured items (`ProductItem`)  
- Modular spiders (per-website)  
- Built-in retries/throttling  

## Quick Start  
```bash  
scrapy crawl amazon -O products.json  
