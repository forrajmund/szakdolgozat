import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf


# ==========================================
# 1. OLDAL BEÁLLÍTÁSAI ÉS STÍLUS
# ==========================================
st.set_page_config(
    page_title="ICT Backtester | Szakdolgozat", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'visited' not in st.session_state:
    st.session_state['visited'] = False

if not st.session_state['visited']:
    # Fejléc dizájnosan középre igazítva
    if not st.session_state['visited']:
        st.markdown("<h1 style='text-align: center;'>🏛️ Algoritmikus Kereskedési és Backtesting Keretrendszer</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>👋 Üdvözöllek a Szimulációs Weboldalamon!</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; color: gray;'>Szakdolgozati demonstrációs szoftver | ICT koncepciók validálása</h5>", unsafe_allow_html=True)
    
    st.divider()
    
    # Részletes, laikusbarát leírás
    st.markdown("""
    ### 📌 Miről szól ez a weboldal?
    Ez a felület egy **automatizált tőzsdei szimulátor**, amely azt hivatott bemutatni, hogyan teljesítene egy előre beprogramozott kereskedési stratégia a múltbeli és aktuális piaci adatokon. A rendszer a professzionális **ICT (Inner Circle Trader)** elméletekre épülő logikát alkalmazza, és teljesen automatikusan azonosítja a lehetséges vételi (Long) és eladási (Short) pontokat.
    
    A cél a laikusok számára is érthetővé tenni a **"backtesting" (visszatesztelés)** folyamatát: megmutatni, hogy egy szigorú matematikai és logikai szabályrendszer alapján működő algoritmus milyen hozamot és kockázatot produkált volna egy adott történelmi időszak alatt, emberi beavatkozás nélkül.
    """)
    
    # Funkciók kiemelt, formázott dobozban
    st.info("""
    **🛠️ Útmutató a felülethez (Mi mit csinál?)**
    
    *   ⚙️ **Bal oldali sáv (Szimulációs Paraméterek):** Itt te magad szabhatod testre a szimulációt. Beállíthatod, hogy mekkora kezdőtőkével és mekkora pozíciómérettel induljon a teszt.
    *   📊 **Főoldali Teljesítmény mutatók:** Gyors és letisztult áttekintést ad az eredményekről (pl. elért nettó profit, nyerési arány, maximális tőkevisszaesés).
    *   📈 **Interaktív Árfolyam grafikon:** Vizuálisan követheted a piac mozgását. A zöld és piros nyilak jelölik a stratégia által generált konkrét belépési és kilépési pontokat.
    *   📋 **Kötésnapló és Visszaesés:** Részletes, táblázatos bizonyíték az összes végrehajtott tranzakcióról, beleszámítva a brókeri jutalékokat is, hogy a végeredmény minél valósághűbb legyen.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Piros, nagybetűs jogi nyilatkozat
    st.error("""
    **🚨 JOGI ÉS KOCKÁZATI FIGYELMEZTETÉS**
    
    **A WEBOLDALON MEGJELENŐ ADATOK, ELEMZÉSEK ÉS EREDMÉNYEK KIZÁRÓLAG OKTATÁSI ÉS DEMONSTRÁCIÓS CÉLOKAT SZOLGÁLNAK, ÉS SEMMILYEN KÖRÜLMÉNYEK KÖZÖTT NEM MINŐSÜLNEK PÉNZÜGYI, BEFEKTETÉSI VAGY KERESKEDÉSI TANÁCSADÁSNAK!** 
    
    A MÚLTBELI TELJESÍTMÉNY NEM GARANCIA A JÖVŐBELI EREDMÉNYEKRE. A TŐZSDEI HATÁRIDŐS (FUTURES) KERESKEDÉS KIFEJEZETTEN KOCKÁZATOS, ÉS A BEFEKTETETT TŐKE TELJES ELVESZTÉSÉVEL IS JÁRHAT. MINDENKI KIZÁRÓLAG A SAJÁT FELELŐSSÉGÉRE, A SAJÁT TŐKÉJÉT KOCKÁZTATVA HOZ BEFEKTETÉSI DÖNTÉSEKET.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gomb középre igazítása oszlopokkal a szebb dizájn érdekében
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Tudomásul vettem / Tovább a szimulációhoz", use_container_width=True, type="primary"):
            st.session_state['visited'] = True
            st.rerun()
            
    st.stop()

    
    st.success("Élő Piaci Szignál: Aktív (Vizuális mód)") # Ide jöhet a te szignál kiírató logikád
# ==========================================
# 2. ÜZLETI LOGIKA (OSZTÁLYOK)
# ==========================================
class ICTStrategy:
    def __init__(self, data):
        self.data = data.copy()
        
    def generate_signals(self):
        self.data['Signal'] = 0
        long_condition = ((self.data['Sweep_Bullish'] == True) | (self.data['Sweep_Bullish'].shift(1) == True)) & (self.data['Break_Up'] == True) & (self.data['Close'] > self.data['VWAP'])
        short_condition = ((self.data['Sweep_Bearish'] == True) | (self.data['Sweep_Bearish'].shift(1) == True)) & (self.data['Break_Down'] == True) & (self.data['Close'] < self.data['VWAP'])
        
        self.data.loc[long_condition, 'Signal'] = 1
        self.data.loc[short_condition, 'Signal'] = -1
        return self.data

class Portfolio:
    def __init__(self, data, initial_capital, contract_multiplier, commission):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.multiplier = contract_multiplier 
        self.commission = commission 
        
    def simulate_trades(self):
        self.data['Position'] = self.data['Signal'].shift(1).fillna(0)
        self.data['Price_Change'] = self.data['Close'] - self.data['Close'].shift(1)
        self.data['PnL'] = self.data['Position'] * self.data['Price_Change'] * self.multiplier
        self.data['Trade_Executed'] = self.data['Position'].diff().abs() > 0
        self.data.loc[self.data['Trade_Executed'], 'PnL'] -= self.commission
        self.data['PnL'] = self.data['PnL'].fillna(0)
        self.data['Equity'] = self.initial_capital + self.data['PnL'].cumsum()
        return self.data

# ==========================================
# 3. ADATLETÖLTÉS (Gyorsítótárazva - Caching)
# ==========================================
@st.cache_data(show_spinner=False)
def load_and_prepare_data(ticker):
    df = yf.download(ticker, interval="1h", period="1y")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.dropna(inplace=True)
    
    # Indikátorok számolása
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    daily_groups = df.groupby(df.index.date)
    df['Cum_Vol'] = daily_groups['Volume'].cumsum()
    df['Cum_Vol_Price'] = (df['Typical_Price'] * df['Volume']).groupby(df.index.date).cumsum()
    df['VWAP'] = df['Cum_Vol_Price'] / df['Cum_Vol']

    asian_session = df.between_time('00:00', '08:00')
    daily_asian_high = asian_session.groupby(asian_session.index.date)['High'].max()
    daily_asian_low = asian_session.groupby(asian_session.index.date)['Low'].min()
    
    df['Asian_High'] = df.index.date
    df['Asian_High'] = df['Asian_High'].map(daily_asian_high)
    df['Asian_Low'] = df.index.date
    df['Asian_Low'] = df['Asian_Low'].map(daily_asian_low)

    window = 5
    df['Local_Max'] = df['High'].rolling(window=window).max().shift(1)
    df['Local_Min'] = df['Low'].rolling(window=window).min().shift(1)
    df['Break_Up'] = (df['Close'] > df['Local_Max']) & (df['Close'].shift(1) <= df['Local_Max'].shift(1))
    df['Break_Down'] = (df['Close'] < df['Local_Min']) & (df['Close'].shift(1) >= df['Local_Min'].shift(1))

    df['Sweep_Bullish'] = (df['Low'] < df['Asian_Low']) & (df['Close'] > df['Asian_Low']) & (df['Open'] > df['Asian_Low'])
    df['Sweep_Bearish'] = (df['High'] > df['Asian_High']) & (df['Close'] < df['Asian_High']) & (df['Open'] < df['Asian_High'])
    return df

# ==========================================
# 4. WEBOLDAL FELÜLET (UI)
# ==========================================
# Két oszlop a fejlécnek: balra megy a cím, jobbra tartjuk a helyet a gombnak
col_title, col_dict = st.columns([5, 1])

with col_title:
    st.title("🏛️ Algoritmikus Kereskedési és Backtesting Keretrendszer")
    st.markdown("Szakdolgozati demonstrációs szoftver | **ICT (Inner Circle Trader) koncepciók validálása határidős piacokon**")

dict_placeholder = col_dict.empty() # Ez a láthatatlan doboz foglalja le a helyet a jobb felső sarokban!

st.divider()

# Oldalsáv (Sidebar)
st.sidebar.header("⚙️ Szimulációs Paraméterek")
# A felhasználó csak egy érthető, nem átírható szöveget lát:
st.sidebar.text_input("Kereskedett Eszköz", value="Micro Nasdaq-100 (Tőzsdei Index)", disabled=True)

# A háttérkód és a Yahoo Finance lekérés számára fixen megadjuk a tikert:
ticker = "MNQ=F"
kezdoto = st.sidebar.number_input("Kezdőtőke (USD)", min_value=1000.0, value=10000.0, step=1000.0)

quantity = st.sidebar.number_input("Kontraktus mennyiség (db)", min_value=1, value=10, step=1)
point_value = st.sidebar.number_input("Pontérték (MNQ = 2 USD/pont)", value=2.0, disabled=True)
# A jutalék/csúszás bemenetet innen teljesen töröltük!

if st.sidebar.button("🚀 Szimuláció Futtatása", type="primary"):
    with st.spinner('Adatelemzés és stratégia validálása folyamatban...'):
        
        df = load_and_prepare_data(ticker) # Ha itt van idősík paramétered, hagyd meg
        strategy = ICTStrategy(df)
        df_signals = strategy.generate_signals()
        
        # A teljes dollárszorzó
        total_multiplier = quantity * point_value
        
        # JAVÍTVA: A 'multiplier' helyett 'total_multiplier', a 'commission' pedig fix 0
        portfolio = Portfolio(df_signals, initial_capital=kezdoto, contract_multiplier=total_multiplier, commission=0)
        df_portfolio = portfolio.simulate_trades()
        
        # Adatok feldolgozása
        df = load_and_prepare_data(ticker)
        
        # Stratégia és Portfólió futtatása
        strategy = ICTStrategy(df)
        df_signals = strategy.generate_signals()
        
        portfolio = Portfolio(df_signals, initial_capital=kezdoto, contract_multiplier=total_multiplier, commission=0)
        df_portfolio = portfolio.simulate_trades()
        
        # Statisztikák számolása
        df_portfolio['Trade_ID'] = df_portfolio['Trade_Executed'].cumsum()
        active_trades = df_portfolio[df_portfolio['Position'] != 0]
        trade_results = active_trades.groupby('Trade_ID')['PnL'].sum()
        
        total_trades = len(trade_results)
        winning_trades = (trade_results > 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        final_equity = df_portfolio['Equity'].iloc[-1]
        net_profit = final_equity - kezdoto
        roi = (net_profit / kezdoto) * 100

       
        with dict_placeholder:
            with st.popover("📖 Fogalomtár"):
                st.markdown("""
                ### 📈 Tőzsdei és Backtesting Alapfogalmak
                * **Backtesting (Visszatesztelés):** Egy kereskedési stratégia múltbeli piaci adatokon történő tesztelése, hogy lássuk, hogyan teljesített volna élesben.
                * **Commission (Jutalék):** A brókercég által a tranzakciókért felszámolt díj. A szimuláció ezt is beleszámolhatja a valósághű eredményekért.
                * **Drawdown (Visszaesés):** A tőke maximális százalékos csökkenése egy adott időszak alatt, a legmagasabb elért ponttól számítva. A stratégia kockázatosságát mutatja.
                * **Equity (Egyenleg):** A kereskedési számla aktuális, valós idejű egyenlege.
                * **Long (Vétel):** Pozíció nyitása az árfolyam emelkedésére számítva. Profitot akkor termel, ha az ár felfelé mozog.
                * **Pip / Pont:** A minimális ármozgás mértékegysége a tőzsdén.
                * **Profit Factor (Profit Tényező):** A bruttó nyereség és a bruttó veszteség aránya. Ha 1 felett van, a stratégia nyereséges.
                * **Sharpe-ráta:** A befektetés kockázattal korrigált hozamát méri. Minél magasabb, annál jobb (az 1 feletti érték már jónak számít).
                * **Short (Eladás):** Pozíció nyitása az árfolyam csökkenésére számítva (shortolás). Profitot akkor termel, ha az árfolyam esik.
                * **Slippage (Csúszás):** A különbség a várt ár és a tényleges végrehajtási ár között, ami a piac gyors mozgása miatt alakulhat ki.
                * **Stop Loss (SL - Veszteségvágó):** Egy előre beállított árszint, ahol a rendszer automatikusan lezárja a pozíciót, hogy megakadályozza a további veszteségeket.
                * **Take Profit (TP - Célár):** Egy előre beállított árszint, ahol a rendszer automatikusan lezárja a pozíciót, realizálva az elért nyereséget.
                * **Ticker (pl. MNQ=F):** A tőzsdei termék egyedi azonosító kódja. Az MNQ=F a Micro E-mini Nasdaq-100 indexet jelöli a határidős piacon.
                * **Win Rate (Nyerési arány):** A nyereséggel zárult tranzakciók aránya az összes tranzakcióhoz képest.
                
                ---
                
                ### 🏛️ ICT / SMC (Intézményi) Fogalmak
                * **BOS (Break of Structure):** Piaci struktúratörés. A trend folytatódását jelzi egy korábbi csúcs vagy mélypont áttörésével.
                * **BSL / SSL (Buy / Sell Side Liquidity):** Vételi és eladási likviditás. Olyan árszintek (korábbi csúcsok és mélypontok), ahol sok lakossági megbízás (Stop Loss) halmozódik fel.
                * **CHoCH (Change of Character):** Karakterváltás. Az első komolyabb jele annak, hogy a jelenlegi trend megfordulhat.
                * **Displacement (Elmozdulás):** Erőteljes, nagy gyertyákkal történő ármozgás, amely gyakran intézményi beavatkozásra utal, és FVG-ket hagy maga után.
                * **FVG (Fair Value Gap - Méltányos érték rés):** Jelentős, hirtelen árfolyam-elmozdulás után keletkező űr a grafikonon, amelyet a piac a későbbiekben gyakran hajlamos "betölteni".
                * **ICT / SMC (Inner Circle Trader / Smart Money Concepts):** Intézményi kereskedési módszertanok, amelyek a nagy szereplők ("okos pénz") feltételezett piaci mozgásait próbálják lekövetni.
                * **Killzone:** Konkrét időszakok a nap folyamán (pl. London vagy New York nyitás), amikor a legnagyobb a piaci volumen és a legkiszámíthatóbbak az intézményi mozgások.
                * **OB (Order Block - Megbízási blokk):** Egy olyan zóna (gyertya), ahol a nagy intézményi szereplők korábban jelentős mennyiségű pozíciót építettek ki.
                * **OTE (Optimal Trade Entry):** Optimális belépési pont. A Fibonacci szintek alapján (általában 62% és 79% között) meghatározott ideális zóna a pozíciónyitásra.
                """)
        
        rolling_max = df_portfolio['Equity'].cummax()
        drawdown = (df_portfolio['Equity'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        daily_equity = df_portfolio['Equity'].resample('D').last().dropna()
        daily_returns = daily_equity.pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if len(daily_returns) > 1 else 0

        # --- EREDMÉNYEK MEGJELENÍTÉSE (KPI Kártyák) ---
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Záró Egyenleg", f"${final_equity:,.2f}", f"{roi:.2f}% Hozam")
        col2.metric("Nettó Profit", f"${net_profit:,.2f}")
        col3.metric("Nyerési Arány (Win Rate)", f"{win_rate:.2f}%")
        col4.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        col5.metric("Sharpe-ráta", f"{sharpe_ratio:.2f}")
        
        st.divider()

        # --- FÜLES ELRENDEZÉS (TABS) ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Grafikonok és Árfolyam", 
            "📉 Visszaesés (Drawdown)", 
            "📋 Kötésnapló", 
            "📖 Módszertan", 
            "🔴 Élő Piaci Szignál"
        ])
        
        with tab1:
            st.subheader("Interaktív Árfolyam grafikon")
            
            fig = go.Figure()
            
            # Gyertyatartó grafikon TradingView stílusú színekkel
            fig.add_trace(go.Candlestick(
                x=df_portfolio.index, 
                open=df_portfolio['Open'], 
                high=df_portfolio['High'], 
                low=df_portfolio['Low'], 
                close=df_portfolio['Close'], 
                name='Árfolyam',
                increasing_line_color='#089981', # Határozott TradingView zöld
                decreasing_line_color='#f23645'  # Határozott TradingView piros
            ))
            
            # Vételi jelek (Long)
            buy_signals = df_portfolio[df_portfolio['Signal'] == 1]
            fig.add_trace(go.Scatter(
                x=buy_signals.index, y=buy_signals['Low'] - 20, 
                mode='markers', marker=dict(symbol='triangle-up', color='lightgreen', size=12, line=dict(color='black', width=1)), 
                name='Vétel (Long)'
            ))
            
            # Eladási jelek (Short)
            sell_signals = df_portfolio[df_portfolio['Signal'] == -1]
            fig.add_trace(go.Scatter(
                x=sell_signals.index, y=sell_signals['High'] + 20, 
                mode='markers', marker=dict(symbol='triangle-down', color='red', size=12, line=dict(color='black', width=1)), 
                name='Eladás (Short)'
            ))
            
        
            # Új elrendezés: Letisztult TradingView stílusú címke, gombok nélkül
            fig.update_layout(
                height=700,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=40, b=10), # Felső margó visszavétele, mivel nincsenek gombok
                yaxis=dict(
                    tickformat=".0f",
                    side="right",
                    title="Árfolyam"
                ),
                xaxis=dict(
                    type="date",
                    rangebreaks=[dict(bounds=["sat", "mon"])] # Hétvégék (üresjáratok) elrejtése a folyamatos idővonalhoz
                ),
                annotations=[
                    dict(
                        x=0.01, y=0.98, 
                        xref="paper", yref="paper",
                        text="<span style='font-size:14px; color:#d1d4dc;'>Micro E-mini Nasdaq-100 (MNQ) · 1h · CME</span>",
                        showarrow=False,
                        xanchor="left", yanchor="top",
                        bgcolor="rgba(19, 23, 34, 0.8)",
                        bordercolor="rgba(41, 98, 255, 0.7)", 
                        borderwidth=1,
                        borderpad=6
                    )
                ]
            )
            st.plotly_chart(fig, use_container_width=True)
           

        with tab2:
            st.subheader("Tőkevisszaesés (Underwater Curve)")
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown * 100, mode='lines', fill='tozeroy', line=dict(color='red'), name='Drawdown %'))
            fig_dd.update_layout(height=400, template="plotly_dark", yaxis_title="Visszaesés (%)")
            st.plotly_chart(fig_dd, use_container_width=True)

        with tab3:
            st.subheader("Végrehajtott Tranzakciók (Kereskedési Napló)")
            
            trades = []
            entry_time = None
            entry_price = 0.0
            position_side = 0
            
            # Kigyűjtjük azokat a pontokat, ahol tranzakció történt
            executed_trades = df_portfolio[df_portfolio['Trade_Executed'] == True]
            
            for time, row in executed_trades.iterrows():
                current_pos = row['Position']
                
                # ZÁRÁS: Ha volt nyitott pozíciónk és most bezárjuk (vagy fordul az irány)
                if position_side != 0 and current_pos != position_side:
                    exit_price = row['Open'] # A kilépés mindig az adott gyertya nyitóárán történik
                    
                    # A jutalék (- commission) levonását töröltük, és bekerült a total_multiplier
                    trade_pnl = (exit_price - entry_price) * position_side * total_multiplier
                    
                    trades.append({
                        'Instrument': ticker.split('=')[0],
                        'Open time': entry_time.strftime('%Y-%m-%d %H:%M'),
                        'Close time': time.strftime('%Y-%m-%d %H:%M'),
                        'Side': 'Long' if position_side == 1 else 'Short',
                        'Quantity': int(quantity), 
                        'Entry Price': entry_price,
                        'Exit Price': exit_price,
                        'Net P&L': trade_pnl
                    })
                    
                    position_side = 0 # Pozíció nullázása a zárás után
                    
                # NYITÁS: Ha nincs nyitott pozíció, és az új nem nulla, akkor belépünk
                if position_side == 0 and current_pos != 0:
                    position_side = current_pos
                    entry_time = time
                    entry_price = row['Open']

            # Táblázat (DataFrame) létrehozása a formázott adatokból
            df_trades = pd.DataFrame(trades)
            
            if not df_trades.empty:
                st.write(f"**Összes lezárt kötés:** {len(df_trades)} db")
                
                # Egyedi színezés a P&L és a Side oszlopokhoz (Zöld/Piros)
                def style_logic(val):
                    if isinstance(val, (int, float)):
                        return 'color: #00fa9a;' if val > 0 else ('color: #ff4b4b;' if val < 0 else '')
                    if val == 'Long':
                        return 'color: #00fa9a;'
                    if val == 'Short':
                        return 'color: #ff4b4b;'
                    return ''

                styled_df = df_trades.style.format({
                    'Entry Price': '${:.2f}',
                    'Exit Price': '${:.2f}',
                    'Net P&L': '${:.2f}'
                }).map(style_logic, subset=['Net P&L', 'Side'])
                
                # Megjelenítés sorszámok (index) elrejtésével
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("Nincs megjeleníthető lezárt tranzakció.")

        with tab4:
            st.subheader("Az alkalmazott ICT / SMC Stratégia Logikája és Architektúrája")
            
            st.markdown("""
            Ez a szimulációs keretrendszer az **Inner Circle Trader (ICT)** és a **Smart Money Concepts (SMC)** 
            árképzési modelljeinek algoritmikus leképezésén alapul. A stratégia célja, hogy a kiskereskedelmi (retail) 
            piaci szereplők likviditásának begyűjtését követően, az intézményi tőke (Smart Money) mozgásával egy irányban vegyen fel pozíciókat.
            """)
            
            st.divider()
            
            st.markdown("### 🔍 A Belépési Szignál Felépítése (Lépésről Lépésre)")
            st.markdown("Az algoritmus egy szigorú, 3 lépcsős feltételrendszert vizsgál. Az alábbiakban egy **Long (Vételi)** pozíció kialakulását szemléltetjük.")
            
            # Vizuális szemléltetés (ASCII Art / Folyamatábra) a Streamlit kódblokkjával
            st.code(r"""
      [3] CHoCH (Market Structure Shift)
             /|        
            / |       /  <-- [4] ENTRY (Belépés a VWAP felett)
           /  |      / 
    ------/---|-VWAP/----------- (Intézményi Átlagár)
         /    |    /   
    \   /     |   /
     \ /      |  /
    --x-------|--x-------------- SSL (Sell-Side Liquidity / Ázsiai mélypont)
      |        \ /
      |         | <-- [2] Hamis kitörés, Stop-Lossok kiütése
     [1]       Sweep (Likviditás begyűjtés)
            """, language="text")

            # Háromoszlopos elrendezés a lépések részletes magyarázatához
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.error("""
                **1. Liquidity Sweep (Vadászat)**  
                **Célpont:** Ázsiai mélypont (SSL).  
                **Logika:** A piac szándékosan bezuhan a korábbi támasz alá. Itt aktiválódnak a kiskereskedők eladási (Sell Stop) megbízásai. 
                A Smart Money ezt a hirtelen jövő eladói likviditást használja fel arra, hogy hatalmas mennyiségű vételi pozíciót építsen ki anélkül, hogy az árat túl korán felvinné.
                """)
                
            with col2:
                st.warning("""
                **2. CHoCH / BOS (Struktúra Törés)**  
                **Célpont:** Korábbi lokális csúcs.  
                **Logika:** A puszta leszúrás nem elég. Várjuk a "Displacement"-et (erőteljes elmozdulást). 
                Ha az árfolyam a leszúrás után agresszívan megfordul, és egy korábbi ellenállás (5-ös ablakú csúcs) felett zár, 
                az megerősíti, hogy az intézmények átvették az irányítást (Change of Character).
                """)

            with col3:
                st.success("""
                **3. VWAP Szűrő (Belépés)**  
                **Célpont:** Intézményi átlagár.  
                **Logika:** A pozíció felvételének utolsó feltétele. Long jelzés esetén az árfolyamnak a 
                napi Volumen-súlyozott Átlagár (VWAP) felett kell elhelyezkednie. Ez az indikátor a volumen alapján 
                mutatja a valós piaci egyensúlyt; a felette lévő árfolyam erős bika trendet igazol.
                """)
                
            st.divider()
            
            st.markdown("### 🔄 Piaci Irányok Logikája")
            col_long, col_short = st.columns(2)
            with col_long:
                st.success("**VÉTEL (LONG) SZABÁLYOK:**\n1. Árfolyam az Ázsiai mélypont alá szúr (Sweep)\n2. Gyertya a korábbi lokális csúcs felett zár (CHoCH)\n3. Árfolyam > VWAP (Trend megerősítése)")
            with col_short:
                st.error("**ELADÁS (SHORT) SZABÁLYOK:**\n1. Árfolyam az Ázsiai csúcs fölé szúr (Sweep)\n2. Gyertya a korábbi lokális mélypont alatt zár (CHoCH)\n3. Árfolyam < VWAP (Trend megerősítése)")

            st.divider()
            
            # Lenyitható panel a matematikai képleteknek
            with st.expander("🧮 Matematikai háttér: A VWAP (Volume Weighted Average Price) számítása"):
                st.markdown("Az algoritmus napi szinten újrainduló (Anchored) VWAP-ot használ, az alábbi képlet alapján:")
                st.latex(r"""VWAP = \frac{\sum_{i=1}^{n} (P_i \times V_i)}{\sum_{i=1}^{n} V_i}""")
                st.markdown("""
                * **$P_i$**: A *Típusos Ár* (Typical Price): $(High + Low + Close) / 3$
                * **$V_i$**: A kereskedett volumen (Volume).
                * **$n$**: A napi kereskedési ciklus kezdete óta eltelt periódusok száma.
                """)

        with tab5:
            st.subheader("🔴 Valós Idejű Piaci Figyelő")
            st.markdown("Az algoritmus a legutolsó letöltött gyertya alapján elemzi a jelenlegi piaci állapotot.")
            
            # A legutolsó sor (legfrissebb adat) kinyerése a DataFrame-ből
            last_candle = df_portfolio.iloc[-1]
            # Időzóna konvertálása magyar időre (New York -> Budapest)
            ny_time = df_portfolio.index[-1].tz_localize('America/New_York')
            hu_time = ny_time.tz_convert('Europe/Budapest')
            last_time = hu_time.strftime("%Y-%m-%d %H:%M")
            
            st.write(f"**Utolsó frissítés (gyertya zárása):** {last_time}")
            
            # Élő adatok megjelenítése 3 oszlopban
            lc1, lc2, lc3 = st.columns(3)
            lc1.metric("Aktuális Árfolyam (Close)", f"{last_candle['Close']:.2f}")
            lc2.metric("Napi VWAP", f"{last_candle['VWAP']:.2f}")
            lc3.metric("Ázsiai Minimum (Low)", f"{last_candle['Asian_Low']:.2f}")


            # 1. A felugró ablak designjának definiálása (alapból ad hozzá egy X gombot a jobb felső sarokba)
            @st.dialog("🔔 Figyelem: Új Piaci Szignál!")
            def felugro_ablak(signal, ar):
                if signal == 1:
                    st.success(f"**VÉTEL (Long)** szignál a piacon!\n\nZáróár: {ar:.2f} USD")
                elif signal == -1:
                    st.error(f"**ELADÁS (Short)** szignál a piacon!\n\nZáróár: {ar:.2f} USD")
                st.info("A folytatáshoz zárd be az ablakot a jobb felső X-szel.")


            # 2. --- Élő Piaci Szignál Vizuális Értesítő ---
            utolso_signal = last_candle['Signal']
            #utolso_signal = 1 # Ideiglenes teszteléshez vedd ki a # jelet

            # Memória inicializálása, hogy ne ugorjon fel percenként
            if 'ablak_megjelent' not in st.session_state:
                st.session_state.ablak_megjelent = False

            st.markdown("### 🔔 Aktuális Szignál Állapot")
            if utolso_signal == 1:
                st.success(f"Élő szignál: **VÉTEL (Long)** a legutolsó záróáron: {last_candle['Close']:.2f}")
                if not st.session_state.ablak_megjelent:
                    felugro_ablak(1, last_candle['Close'])
                    st.session_state.ablak_megjelent = True
        
            elif utolso_signal == -1:
                st.error(f"Élő szignál: **ELADÁS (Short)** a legutolsó záróáron: {last_candle['Close']:.2f}")
                if not st.session_state.ablak_megjelent:
                    felugro_ablak(-1, last_candle['Close'])
                    st.session_state.ablak_megjelent = True
        
            else:
                st.info("Jelenleg nincs aktív vételi vagy eladási szignál a piacon.")
                # Ha megszűnik a szignál, nullázzuk a memóriát a következő alkalomra
                st.session_state.ablak_megjelent = False

            st.divider()


        # --- Manuális Adatfrissítés ---
        if st.button("🔄 Szimuláció frissítése", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

else:
    st.info("👈 Kérlek, indítsd el a szimulációt az oldalsávon található gombbal!")