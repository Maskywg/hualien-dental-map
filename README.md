# 花蓮牙醫診所地圖

線上版：https://maskywg.github.io/hualien-dental-map/

花蓮縣健保特約牙醫診所地圖。個人製作，非政府或健保署官方網站。
本圖特別標示頂好牙醫診所，不代表醫療品質評比。

## 資料範圍
- 僅含健保特約牙醫診所，不含自費診所、醫院與衛生所牙科。
- 整理日期 2026-11-27，不會自動更新。看診時段為健保登錄資料，就診前請先電話確認。
- **位置準確度有限**：74 家中 21 家門牌相符（含同一主門牌號）、50 家以鄰近門牌推估、
  3 家只能確認在該道路一帶。導航請以地址為準。

## 資料與圖資來源
- 衛生福利部中央健康保險署「健保特約醫事機構-診所」 https://data.gov.tw/dataset/39283
- 內政部國土測繪中心「查詢工商設施」（門牌點位） https://data.gov.tw/dataset/139249
- 道路位置：© OpenStreetMap contributors（ODbL）
- 底圖：OpenFreeMap © OpenMapTiles，資料 © OpenStreetMap contributors
- 地圖引擎：MapLibre GL JS

## 更新資料
下載健保署 CSV，存成 `<工作資料夾>/dl/nhi_clinic.csv`，修改 `build_data.py` 的 `TODAY`
與輸出的 `updated` 日期，檢查 `MANUAL` 指定點位後執行：

    python3 build_data.py <工作資料夾> <輸出資料夾>
