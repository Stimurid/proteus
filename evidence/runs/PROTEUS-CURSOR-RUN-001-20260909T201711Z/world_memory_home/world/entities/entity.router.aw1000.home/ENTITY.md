# Arcadian AW1000 router

- entity_id: `entity.router.aw1000.home`
- aliases: AW1000, our router, Arcadian AW1000

## Current facts

- Secret reference recorded: secret://router.aw1000.home.admin (AW1000 admin)  
  - claim_id: `claim.7f5c15b2e7ef`  
  - provenance: imported_reference / origin-pilot  


- Onlime LAN segment uses 192.168.3.0/24 (ath1 / br-iot) and is treated as DIRECT path; NM VPN path is 192.168.2.0/24 (ath0 / br-lan).  
  - claim_id: `claim.197c538b75e5`  
  - provenance: imported_reference / origin-pilot / C:\projects\.cursor\rules\aw1000-network.mdc + aw1000-audit workspace constraints  

## Notes

Rich prose may live here; structured claims live in `claims.jsonl`.
