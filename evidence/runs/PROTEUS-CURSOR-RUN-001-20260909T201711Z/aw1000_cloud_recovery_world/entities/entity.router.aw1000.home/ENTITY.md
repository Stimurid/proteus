# Arcadian AW1000 router

- entity_id: `entity.router.aw1000.home`
- aliases: AW1000, our router, Arcadian AW1000, Arcadyan AW1000, QWRT, home router, наш роутер

## Current facts

- PROTEUS-AW1000-CLOUD-MARKER-20260911 non-sensitive reconciliation marker.  
  - claim_id: `claim.e9d2c3b0a9d1`  
  - provenance: observation / origin-aw1000-hardening / aw1000_real_entity_episode  

- Live 2026-09-11 revalidated firmware identity: OpenWrt 21.02-SNAPSHOT BUILD_ID=r47273-b4df38cf18 board=ipq807x/generic arch=aarch64_cortex-a53; ubus hostname=QWRT.  
  - claim_id: `claim.9ffe9145edc7`  
  - provenance: observation / origin-aw1000-hardening / C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\AW1000_READONLY_SSH.txt  

- Live 2026-09-11 main table shows default via eth4 metric 10 and via wwan0 metric 20 (plus an additional default via wwan0 without metric in snapshot). Dual-default/mwan state needs ongoing care; do not treat as eternal.  
  - claim_id: `claim.23cdcb47eb88`  
  - provenance: observation / origin-aw1000-hardening / C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\AW1000_READONLY_SSH.txt  

- Live 2026-09-11: eth4 UP with IPv4 188.32.115.18/19; wwan0 UP; br-lan 192.168.2.1/24; br-iot 192.168.3.1/24; awg0 10.8.1.4/32 present.  
  - claim_id: `claim.e3b4d633a175`  
  - provenance: observation / origin-aw1000-hardening / C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\AW1000_READONLY_SSH.txt  

- 2026-09-11T10:00Z approx: SSH root@192.168.3.1 reachable via id_rsa_aw1000; hostname QWRT; OpenWrt 21.02-SNAPSHOT r47273-b4df38cf18 confirmed live.  
  - claim_id: `claim.05e1a5296c9f`  
  - provenance: observation / origin-aw1000-hardening / C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\AW1000_READONLY_SSH.txt  

- As of 2026-09-10 STATUS: Clash/OpenClash removed; AmneziaWG awg0 peer 10.8.1.4 endpoint 130.17.29.18:2066; NM 192.168.2.0/24 via tunnel; onlime 192.168.3.0/24 DIRECT untouched.  
  - claim_id: `claim.d1c7486578fe`  
  - provenance: imported_reference / origin-aw1000-hardening / C:\projects\aw1000-audit\STATUS.md + MIGRATION-STATUS.md  

- Agent SSH management path when PC is on onlime: root@192.168.3.1 using RSA key %USERPROFILE%\.ssh\id_rsa_aw1000 (dropbear requires ssh-rsa). Helper: C:\projects\aw1000-audit\ssh-aw1000.cmd  
  - claim_id: `claim.f3e244b00b87`  
  - provenance: imported_reference / origin-aw1000-hardening / C:\projects\aw1000-audit\SSH-HANDOFF.md  

- Historical diagnostic mapping: upstream Ethernet corresponded to Linux eth4; logical OpenWrt interface WAN_ETH was created as DHCP client on eth4. Names wan/wanb/WAN_ETH are not reliable role labels without live map.  
  - claim_id: `claim.4384b8bba2ff`  
  - provenance: imported_reference / origin-aw1000-hardening / Drive handoff 1lM9BTn1... §3  

- USB modem identified as Quectel ID 2c7c:0800; mobile Linux interface wwan0; control path /dev/cdc-wdm0; mmcli not present.  
  - claim_id: `claim.2f697980c5d1`  
  - provenance: imported_reference / origin-aw1000-hardening / Drive handoff 1lM9BTn1... §2  

- On 2026-08-30 live read: OpenWrt 21.02-SNAPSHOT r47273-b4df38cf18; OPENWRT_BOARD=ipq807x/generic; OPENWRT_ARCH=aarch64_cortex-a53. Treat as historical unless revalidated.  
  - claim_id: `claim.2bd4952d98b2`  
  - provenance: imported_reference / origin-aw1000-hardening / Drive handoff 1lM9BTn1... §1 os-release  

- Device is Arcadyan AW1000; web UI brand is QWRT (OpenWrt-based).  
  - claim_id: `claim.c3eb0e10d195`  
  - provenance: imported_reference / origin-aw1000-hardening / Drive handoff 1lM9BTn1vecgVlWbtN1K14acgzS0nEjn_vZceaQSiLyQ §1  

- Secret reference recorded: secret://router.aw1000.home.admin (AW1000 admin)  
  - claim_id: `claim.7f5c15b2e7ef`  
  - provenance: imported_reference / origin-pilot  


- Onlime LAN segment uses 192.168.3.0/24 (ath1 / br-iot) and is treated as DIRECT path; NM VPN path is 192.168.2.0/24 (ath0 / br-lan).  
  - claim_id: `claim.197c538b75e5`  
  - provenance: imported_reference / origin-pilot / C:\projects\.cursor\rules\aw1000-network.mdc + aw1000-audit workspace constraints  

## Notes

Rich prose may live here; structured claims live in `claims.jsonl`.
