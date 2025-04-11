# 3xpl.com JSON API MCP server

# Overview

3xpl API in form of a Model Context Protocol (MCP) server.

Allows LLMs to interact with data on **48** blockchains.

## List of available tools

| name                                | description                                                                                                    |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------|
| resolve_ens_domain                  | resolves an ENS domain to a regular address                                                                    |
| detect_blockchains                  | retrieve a list of blockchains on which a transaction/address is present                                       |
| get_transaction_info                | get transaction information with provided hash in specified blockchain                                         | 
| get_address_info                    | retrieve information for provided address in specified blockchain                                              | 
| get_batch_addresses_info            | retrieve information for provided multiple addresses in specified blockchain                                   |
| get_block_info                      | get block info by height in provided blockchain                                                                | 
| get_latest_block                    | get latest block height in specified blockchain                                                                | 
| get_average_fee_24h_usd             | retrieves average transaction fee for last 24 hours in specified blockchain                                    |
| get_exchange_rate                   | retrieve exchange rate for native currency in specified blockchain for current moment in provided fiat ticker* |
| get_transaction_count_24h           | retrieve number of transactions in last 24h for provided blockchain                                            |
| get_address_transactions_for_period | retrieve the transaction of an address for a certain period of time - segment                                  |

[//]: # (                           | supported_blockchains                                                                                          | get list of support blockchains by 3xpl API |)

[//]: # (## List of prompts)

[//]: # (| name                   | description                                               |)

[//]: # (|------------------------|-----------------------------------------------------------|)

[//]: # (| analyze_address_prompt | prompt for providing helpful information about an address |)

[//]: # (## List of resources)

[//]: # (| name                       | description                                               |)

[//]: # (|----------------------------|-----------------------------------------------------------|)

[//]: # (| transactions_endpoint_docs | detailed documentation of `/transaction` endpoint on 3xpl |)


*might be inaccurate, see the API docs and policy for details.

## Contribution

Feel free to open issues for bugs or suggestions.  
Pull requests are also welcome – just make sure to provide description of your changes.