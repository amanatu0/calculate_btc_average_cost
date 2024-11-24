import pandas as pd
from collections import deque

def calculate_btc_average_cost():
    # CSVファイルを読み込む
    df = pd.read_csv('TradeHistory.csv', encoding='utf-8')
    
    # 必要な列だけを抽出し、数値型に変換
    df = df[['取引種別', '通貨1', '通貨1数量', '取引価格', '取引日時']]
    df['通貨1数量'] = pd.to_numeric(df['通貨1数量'].str.replace(',', ''), errors='coerce')
    df['取引価格'] = pd.to_numeric(df['取引価格'].str.replace(',', ''), errors='coerce')
    df['取引日時'] = pd.to_datetime(df['取引日時'])
    df = df.sort_values('取引日時')
    
    # BTC取引のみをフィルタリング
    btc_df = df[df['通貨1'] == 'BTC']
    
    # 購入履歴を管理するキュー
    buy_queue = deque()
    current_position = 0.0
    total_cost = 0.0
    
    for _, row in btc_df.iterrows():
        amount = float(row['通貨1数量'])
        price = float(row['取引価格'])
        
        if row['取引種別'] == '買い':
            # 購入の場合
            buy_queue.append({'amount': amount, 'price': price})
            current_position += amount
            total_cost += amount * price
            
        elif row['取引種別'] == '売り':
            # 売却の場合
            remaining_sell = amount
            
            while remaining_sell < 0 and buy_queue:
                oldest_buy = buy_queue[0]
                if oldest_buy['amount'] <= remaining_sell:
                    # 購入ロットを全て売却
                    remaining_sell += oldest_buy['amount']
                    total_cost += oldest_buy['amount'] * oldest_buy['price']
                    current_position += oldest_buy['amount']
                    buy_queue.popleft()
                else:
                    # 購入ロットの一部を売却
                    oldest_buy['amount'] += remaining_sell
                    total_cost += remaining_sell * oldest_buy['price']
                    current_position += remaining_sell
                    remaining_sell = 0
    
    # 平均取得価格を計算
    average_cost = total_cost / current_position if current_position > 0 else 0
    
    return {
        'current_position': current_position,
        'total_cost': total_cost,
        'average_cost': average_cost
    }

if __name__ == '__main__':
    try:
        result = calculate_btc_average_cost()
        print(f"現在のBTC保有量: {result['current_position']:.8f} BTC")
        print(f"取得価格合計: ¥{result['total_cost']:,.0f}")
        if result['current_position'] > 0:
            print(f"平均取得価格: ¥{result['average_cost']:,.0f}/BTC")
        else:
            print("現在のBTC保有はありません")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")