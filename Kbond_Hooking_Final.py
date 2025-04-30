#### GUI로 모니터링 감지하도록 하기.
import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

# === 설정 ===
csv_path = os.path.join(os.getcwd(), 'kbond_log_d1.csv')  # D1 전용 CSV 경로
refresh_interval = 2000  # ms

class KBondMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KBond D1 실시간 모니터")
        self.geometry("1000x600")

        # Treeview 설정
        cols = ['시간','종목코드','상품구분','수익률','민평','대비','수량','만기','구분','판매자']
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor='center')
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 자동 갱신
        self.after(refresh_interval, self.refresh_data)

    def refresh_data(self):
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                # 최대 200개 최신 데이터만 표시
                rows = df.tail(200).values.tolist()
                # 테이블 갱신
                self.tree.delete(*self.tree.get_children())
                for r in rows:
                    # df order: 시간, 종목코드, 상품구분, 수익률, 민평, 대비, 수량, 만기, 구분, 판매자, 화면 + 기타
                    # we only want first 10 columns
                    self.tree.insert('', 'end', values=r[:10])
        except Exception as e:
            print(f"❌ GUI 갱신 오류: {e}")
        finally:
            self.after(refresh_interval, self.refresh_data)

if __name__ == '__main__':
    app = KBondMonitor()
    app.mainloop()
