# 3xpl.com JSON API MCP server

# Overview

3xpl API in form of a Model Context Protocol (MCP) server.

Allows LLMs to interact with data on **48** blockchains.

This repository can also be an example of 3xpl JSON API usage, see details in the code.

[//]: # (demo video from Claude)

## List of available tools

| name                     | description                                                                                                                               | status |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------|
| resolve_ens_domain       | resolves an ENS domain to a regular address                                                                                               | ✅      | 
| detect_blockchains       | retrieve a list of blockchains on which a transaction/address is present                                                                  | ✅      | 
| get_latest_block         | get latest block height in specified blockchain                                                                                           | ✅      |  
| get_average_fee_24h_usd  | retrieves average transaction fee for last 24 hours in specified blockchain in US dollars.                                                | ✅      | 
| get_mempool_events_count | get the number of unconfirmed events(transfers, inputs/outputs, not transactions) at the moment in the memory pool of provided blockchain | ✅      | 
| get_events_count_24h     | retrieve number of events(transfers, inputs/outputs, not whole transactions) in last 24h for provided blockchain                          | ✅      | 
| get_block_overview       | extract short summary about a block in provided blockchain                                                                                | ✅      | 
| get_address_overview     | extract short summary about an address in provided blockchain                                                                             | ✅      | 
| get_transaction_overview | extract short summary about a transaction in provided blockchain                                                                          | ⏳      | 

List will expand soon, stay tuned!

*might be inaccurate, see the API docs and policy for details.

## Contribution

Feel free to open issues for bugs or suggestions.  
Pull requests are also welcome – just make sure to provide description of your changes.