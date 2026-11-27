# 花蓮牙醫診所地圖

線上版：https://maskywg.github.io/hualien-dental-map/

花蓮縣健保特約牙醫診所地圖。個人製作，非政府或健保署官方網站。

## 資料範圍
- 診所清單僅含健保特約牙醫診所，不含自費診所、醫院與衛生所（醫院與衛生所牙科另列於補充資料）。
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

## 補充資料

`extra.json` 收錄醫院牙科、衛生所／衛生室牙科、偏鄉學校巡迴與機構口腔照護（整理日期 2026-11-27，手動維護，不由 `build_data.py` 產生）。各項目標示查證程度與來源；時段會調整，就診前請電話確認。

## 影片

`dingho-video.mp4`（封面 `dingho-poster.jpg`）是頂好牙醫診所的 AI 情境演示影片，從該診所的地圖資訊視窗播放。
