SET_KEYS = True
KEY1 = 0
KEY2 = 0
KEY3 = 0


#####################################################################
#####################################################################
''' SMA MESH PERIOD SCALING COEFFICIENTS '''

Z = 1.000  # Scales Full Mesh; Default = 1.000

_2 = 2.000  # Accepts float inputs for sma periods
_30 = 30.000
_55 = 55.000
_60 = 60.000
_90 = 90.000
_150 = 150.000
# Z allows you to speed up or slow down all sma periods simulateously
# as an expanding/contracting mesh; it also scales hold periods

#####################################################################
#####################################################################
''' ICEBERG CONTROLS '''
#####################################################################
# only backtest two orders at a time else it logs too much
ICEBERG_TEST = False  # ON/OFF to test
ICEBERG_SIMPLE = False  # True for simple version

ICEBERG_MIN = 1.5  # (1.5) min order size
ICEBERG_MAX = 2.5  # (2.5) max order size
ICEBERG_QTY = 2.5  # (2.5) max coexisting orders
ICEBERG_WAIT = 60  # (60) sec delay between orders
ICEBERG_ATTEMPTS = 180  # (180) cycle loop x times before fail
ICEBERG_ALERT = 100  # (100) send email after x attempts
#####################################################################
#####################################################################

import talib
import time as t
import random as r

PAIR = info.primary_pair

LIVE = False
try:
    end = info.end
except:
    LIVE = True
BACKTEST = not LIVE


def initialize():
    if 1:  # save the noobs
        if LIVE:
            if info.interval != 3600:
                log('I recommend 1h tick size when live. ' +
                    'Beware of (fees+margin)^info.tick flash trading risk. ' +
                    'Do as you will.')
                raise Stop()
            if info.primary_pair in [pairs.ltc_usd, pairs.ltc_cny, pairs.ltc_eur, pairs.ltc_btc]:
                log('Honey Badger as tuned can get REKT in a LTC bear market. ' +
                    'Do as you will.')
                raise Stop()

    if SET_KEYS:
        storage.reset()
        log('storage.reset()')

    storage.ratio = n = (43200 / info.interval)

    storage.hold = storage.get('hold', KEY1)
    storage.mode = storage.get('mode', KEY2)
    storage.overbought = storage.get('overbought', KEY3)

    storage.prev_mode = storage.get('prev_mode', 0)
    storage.trades = storage.get('trades', 0)
    storage.action = storage.get('action', 0)
    storage.signal = storage.get('signal', 0)
    storage.currency = storage.get('currency', 0)
    storage.assets = storage.get('assets', 0)
    storage.start_currency = storage.get('start_currency', 0)
    storage.start_assets = storage.get('start_assets', 0)

    if storage.hold + storage.mode + storage.prev_mode > 0:
        if SET_KEYS == True:
            log('New KEYS Installed Successfully: %s %s %s' % (KEY1, KEY2, KEY3))
        if SET_KEYS == False:
            log('Soft Restart Using Stored KEYS: %s %s %s' % (KEY1, KEY2, KEY3))
    else:
        if LIVE:
            # save the noobs
            log('Do not trade live without installing INITIALIZATION KEYS')
            raise Stop()
        if BACKTEST:
            log('No Initialization keys found, the first 3 trades may be innacurate.')


def instruments():
    pair = info.primary_pair
    if pair == pairs.btc_usd:
        pair = 'btcusd'
    if pair == pairs.ltc_usd:
        pair = 'ltcusd'
    if pair == pairs.ltc_btc:
        pair = 'ltcbtc'
    if pair == pairs.btc_eur:
        pair = 'btceur'
    if pair == pairs.ltc_eur:
        pair = 'ltceur'
    if pair == pairs.btc_cny:
        pair = 'btccny'
    if pair == pairs.ltc_cny:
        pair = 'ltccny'
    storage.currency_code = ''.join(list((pair)[3:6]))
    storage.asset_code = ''.join(list((pair)[0:3]))
    storage.currency_CODE = (storage.currency_code).upper()
    storage.asset_CODE = (storage.asset_code).upper()
    return


def ma12h(period, depth):
    minutes = period * 720 * Z

    import math

    if minutes < 2:
        log('minimum period 2 minutes returns 1m data[PAIR].sma(2)')
        minutes = 2
        # raise Stop()
    if minutes > 180000:
        log('maximum period 12h 250 = 180,000 minutes')
        minutes = 180000
        # raise Stop()
    if minutes < 2.0 * info.interval / 60:
        log('select smaller tick size for this FMSMA interval')
        minutes = 2.0 * info.interval / 60
        # raise Stop()

    if 2 <= minutes < 10:
        data_interval = 60
        period = minutes
        depth = depth * 720
    if 10 <= minutes < 20:
        data_interval = 300
        period = minutes / 5
        depth = depth * 144
    if 20 <= minutes < 30:
        data_interval = 600
        period = minutes / 10
        depth = depth * 72
    if 30 <= minutes < 60:
        data_interval = 900
        period = minutes / 15
        depth = 48 * depth
    if 60 <= minutes < 120:
        data_interval = 1800
        period = minutes / 30
        depth = 24 * depth
    if 120 <= minutes < 240:
        data_interval = 3600
        period = minutes / 60
        depth = 12 * depth
    if 240 <= minutes < 480:
        data_interval = 7200
        period = minutes / 120
        depth = 6 * depth
    if 480 <= minutes < 1440:
        data_interval = 14400
        period = minutes / 240
        depth = 3 * depth
    if minutes >= 1440:
        data_interval = 43200
        period = minutes / 720

    period_floor = int(math.floor(period))
    period_ceiling = int(math.ceil(period))

    if period_floor == period_ceiling:
        return float(data(interval=data_interval
                          )[PAIR][depth].ma(period_floor))

    else:

        sma_floor = float(data(
            interval=data_interval)[PAIR][depth].ma(period_floor))
        sma_ceiling = float(data(
            interval=data_interval)[PAIR][depth].ma(period_ceiling))
        ratio = float(period - period_floor)
        inverse = 1 - ratio
        return (ratio * sma_ceiling + inverse * sma_floor)


def chart():
    mode = storage.mode
    if storage.mode < 2:
        mode = 1

    plot('ma2', storage.ma2)
    plot('ma30', storage.ma30)
    plot('floor', storage.floor)
    plot('moon', storage.moon)
    plot('ma60', storage.ma60)
    plot('ma90', storage.ma90)
    plot('ma150', storage.ma150)
    plot('resistance', storage.resistance)

    plot('mode', mode, secondary=True)
    # 1 = green dragon
    # 2 = capitulation
    # 3 = red dragon
    # 4 = cat bounce

    buy = 0
    sell = 0
    if storage.signal == 1:
        buy = 0.5
    if storage.signal == -1:
        sell = -0.5
    plot('buy_signal', buy, secondary=True)
    plot('sell_signal', sell, secondary=True)

    if info.tick == 0:
        plot('offset', -15, secondary=True)


def indicators():
    storage.ma2 = (ma12h(_2, 0))
    storage.ma30 = (ma12h(_30, 0))
    storage.ma55 = (ma12h(_55, 0))
    storage.ma60 = (ma12h(_60, 0))
    storage.ma90 = (ma12h(_90, 0))
    storage.ma150 = (ma12h(_150, 0))

    storage.ma2i = (ma12h(_2, -1))
    storage.ma30i = (ma12h(_30, -1))
    storage.ma55i = (ma12h(_55, -1))
    storage.ma60i = (ma12h(_60, -1))
    storage.ma90i = (ma12h(_90, -1))
    storage.ma150i = (ma12h(_150, -1))

    storage.floor = (1 - (0.25 * Z)) * storage.ma55
    storage.moon = (1 + (0.05 * Z)) * storage.ma55
    storage.resistance = (storage.ma30 + 2.8 *
                          (storage.ma30 - storage.ma60))


def holdings():
    storage.currency = float(portfolio[currencies[storage.currency_code]])
    storage.assets = float(portfolio[currencies[storage.asset_code]])

    if info.tick == 0:
        storage.start_currency = (0.00001 +
                                  storage.currency + storage.assets * storage.ma2)
        storage.start_assets = (0.00001 +
                                storage.assets + storage.currency / storage.ma2)
        if storage.currency + storage.assets == 0:
            log('Zero Starting Portfolio')
            raise Stop()

    storage.holding_assets = False
    storage.holding_currency = False
    if storage.currency > (storage.ma2 * 0.02):
        storage.holding_currency = True
    if storage.assets > 0.12:
        storage.holding_assets = True


def mode_select():
    if storage.hold <= 0:

        ma2 = storage.ma2
        ma30 = storage.ma30
        ma60 = storage.ma60
        ma90 = storage.ma90
        ma150 = storage.ma150
        ma30i = storage.ma30i
        ma60i = storage.ma60i
        ma90i = storage.ma90i
        ma150i = storage.ma150i
        resistance = storage.resistance

        # Green Dragon Market
        if ((ma30 > ma60) and
                (ma60 > ma90) and
                (ma90 > ma150) and
                (ma2 > ma30) and
                (ma30 > 1.002 * ma30i) and
                (ma60 > 1.002 * ma60i) and
                (ma90 > 1.002 * ma90i)):
            storage.mode = 1
            if ma2 > resistance:
                storage.overbought = 4 * 43200
            if storage.overbought > 0:
                storage.overbought -= info.interval
                storage.mode = -1

        # Red Dragon Market
        elif ((resistance < ma150) and
                  (ma2 < ma90) and
                  (ma2 < ma150) and
                  (ma150 < ma150i) and
                  (resistance < ma90)):
            storage.mode = 3

        # Not Dragon Market
        else:
            if storage.prev_mode == (3 or 4):
                storage.mode = 4  # Cat Bounce
            if abs(storage.prev_mode) == (1 or 2):
                storage.mode = 2  # Capitulation


def mode_3():
    ma2 = storage.ma2
    ma2i = storage.ma2i
    ma30 = storage.ma30
    signal = 0
    if ma2 < storage.floor:
        signal = 1
    elif ma2 > storage.moon:
        signal = -1
    elif ((ma2 < ma2i) and
              (ma2 < ma30) and
              (ma2i > ma30)):
        signal = -1
    return signal


def think():
    action = 0
    signal = 0
    mode_select()
    n = storage.ratio
    ma2 = storage.ma2
    hold = storage.hold
    mode = storage.mode
    ma30 = storage.ma30
    ma60 = storage.ma60
    ma90 = storage.ma90
    ma90i = storage.ma90i
    ma150 = storage.ma150
    prev_mode = storage.prev_mode
    holding_assets = storage.holding_assets
    holding_currency = storage.holding_currency

    if hold <= 0:

        # MODE <2 - GREEN DRAGON
        if mode == 0:
            signal = 1
            hold = 1
            if holding_currency:
                log('CRYPTO LONG')
                action = 1
                hold = 1
        if mode == 1:
            signal = 1
            hold = 1
            if holding_currency:
                log('GREEN DRAGON')
                action = 1
                hold = 1
        if mode == -1:
            signal = -1
            hold = 0
            if holding_assets:
                log('OVERBOUGHT')
                action = -1
                hold = 1

        # MODE 2 - CAPITULATION
        if ((mode == 2) and (prev_mode != 2)):
            signal = -1
            if holding_assets:
                log('CAPITULATION')
                action = -1
                hold = 1
        if mode == prev_mode == 2:
            if ma2 < ma90:
                signal = 1
                if holding_currency:
                    log('DESPAIR')
                    action = 1
                    hold = 1
            if ((ma2 > (1.1 * ma90)) and
                    (ma2 > ma60)):
                signal = -1
                if holding_assets:
                    log('FINAL RUN OF THE BULLS')
                    action = -1
                    hold = 2

        # MODE 3 - RED DRAGON
        if ((mode == 3) and (prev_mode != 3)):
            signal = -1
            hold = 0
            if holding_assets:
                log('RED DRAGON')
                action = -1
                hold = 5
        if mode == prev_mode == 3:
            signal_3 = mode_3()
            if signal_3 == 1:
                signal = 1
                hold = 5
                if holding_currency:
                    log('PURGATORY')
                    action = 1
                    hold = 5
            elif signal_3 == -1:
                signal = -1
                hold = 0
                if holding_assets:
                    log('DEEPER')
                    action = -1
                    hold = 1

        # MODE 4 - CAT BOUNCE
        if ((mode == 4) and (prev_mode != 4)):
            signal = 1
            hold = 0
            if holding_currency:
                log('HONEY')
                action = 1
                hold = 2
        if mode == prev_mode == 4:
            if ((ma2 < 1.05 * ma30) and
                    (ma2 > ma60) and
                    (ma90 > 1.003 * ma90i)):
                signal = -1
                hold = 1
                if holding_assets:
                    log('KARMA')
                    action = -1
                    hold = 1
            if ((ma2 < ma90) and
                    (ma90 < ma60) and
                    (ma90 < ma30) and
                    (ma90 > ma90i)):
                signal = 1
                hold = 0
                if holding_currency:
                    log('GOLD')
                    action = 1
                    hold = 1

        storage.hold = Z * hold * 86400

    storage.hold -= info.interval
    storage.signal = signal
    storage.action = action
    storage.prev_mode = storage.mode


def order():
    if storage.action == 1:
        if storage.holding_currency:
            market_ice(buy)
            storage.trades += 1
            email(data[PAIR].price,
                  subject='**ALERT** HONEY BADGER SAYS: BUY OR CRY')

    if storage.action == -1:
        if storage.holding_assets:
            market_ice(sell)
            storage.trades += 1
            email(data[PAIR].price,
                  subject='**ALERT** HONEY BADGER SAYS: FIAT TIME')

    if abs(storage.action) == 1:
        report()


def market_ice_simple(action):
    # logical theory is the same in configurable version
    while 1:
        try:
            action(PAIR, amount=2, timeout=60)
        except TradewaveFundsError:
            try:
                portfolio.update()
                action(PAIR)
                break
            except TradewaveInvalidOrderError:
                break
            except:
                pass
        except:
            pass
        if LIVE: t.sleep(60)


def market_ice_banner():
