#!/usr/local/bin/env python
'''
given imput csv, enhance the fields and write to the output with additional columns

additional fields to add:
    SymbolBought: # of shares of stock bought
    SymbolSold: # of shares of stock sold
    SymbolPosition: Long (bought > sold)/Short (sold > bought)/Flat (sold == bought)
    SymbolNotional: FillSize * FilledPrice
    ExchangeBought: # of shares bought on current exchange, across all symbols
    ExchangeSold: same as above but for sold
    TotalBought: sum of all SymbolBought
    TotalSold: sum of all SymbolSold
    TotalBoughtNotional: total SymbolNotional of all shares bought across all symbols
    TotalSoldNotional: total SymbolNotional of all share sold

Summary stats:
    Shares bought: total # of shares bought
    Shares sold: total # of shares sold
    Notional bought: total # of all share bought

Notes:
    solutions should calculate the values during the readfile
    all notional and price based values should be to 2 decimals

Need to have:
    source code
    instruction
    output csv
    output summary stats (stdout)
    others
'''

import csv, argparse
import pdb


def _calculate_median(fill_size_list):
    # though we can easily use numpy, I try to avoid using 3rd party lib
    if len(fill_size_list) % 2 == 1:
        return fill_size_list[(len(fill_size_list) + 1) / 2 + 1]
    else:
        lower = fill_size_list[len(fill_size_list) / 2 - 1]
        upper = fill_size_list[len(fill_size_list) / 2]
        return (float(lower + upper)) / 2


def _print_summary(count, symbol_track, exchange_track, total_track, fill_size_list):
    top_ten = [(v['Bought'] + v['Sold'], k) for k, v in symbol_track.iteritems()]
    top_ten.sort(reverse=True)
    top_ten = top_ten[:10]
    top_ten = ', '.join('%s(%s)' % (sym, vol) for vol, sym in top_ten)

    print('Processed Trades: %s' % count)
    print('\n')
    print('Shares Bought: %s' % total_track['Bought'])
    print('Shares Sold: %s' % total_track['Sold'])
    print('Total Volume: %s' % sum([total_track['Bought'], total_track['Sold']]))
    print('Notional Bought: %s' % total_track['BoughtNotional'])
    print('Notional Sold: %s' % total_track['SoldNotional'])
    print('\n')
    print('Per Echange Volume:')
    for k, v in exchange_track.iteritems():
        print('%s Bought: %s' % (k, v['Bought']))
        print('%s Sold: %s' % (k, v['Sold']))
    print('Averge Trade Size: %.2f' % (float(sum([total_track['Bought'], total_track['Sold']])) / count))
    print('Midian Trade Size: %s' % _calculate_median(fill_size_list))
    print('10 Most Active Symbols: %s' % top_ten)


def calcTradeStats(inputFile, outputFile):
    '''
    function to parse data from inputFile and write the same columns plus some enhance info into outputFile

    Args:
        inputFile(str): file path that leads to input file. File should be in csv format
        outputFile(str): file name that should be created for writing the processed info
    '''
    try:
        with open(inputFile, 'rb') as csvfile, open(outputFile, 'w') as outfile:
            trade_reader = csv.DictReader(csvfile)
            # setup the headers and write to output file
            field_names = ['LocalTime', 'Symbol', 'EventType', 'Side', 'FillSize', 'FillPrice', 'FillExchange',
                           'SymbolBought', 'SymbolSold', 'SymbolPosition', 'SymbolNotional', 'ExchangeBought',
                           'ExchangeSold', 'TotalBought', 'TotalSold', 'TotalBoughtNotional', 'TotalSoldNotional']
            trade_writer = csv.DictWriter(outfile, fieldnames=field_names)
            trade_writer.writeheader()
            # dict's used for tracking values for symbol bought/sold, exchange bought/sold, and totals
            symbol_track = {}
            exchange_track = {}
            total_track = {'Bought': 0, 'Sold': 0, 'BoughtNotional': 0, 'SoldNotional': 0}
            count = 0
            fill_size_list = []
            # skip header
            #next(trade_reader, None)
            for row in trade_reader:
                # process each row here
                temp_row = row
                if not temp_row.get('FillSize'):
                    # there are some missing values in trades.csv, so need to ignore those
                    continue
                temp_row['FillSize'] = int(temp_row['FillSize'])
                temp_row['FillPrice'] = float(temp_row['FillPrice'])
                # SymbolBought
                if temp_row['Symbol'] in symbol_track:
                    if symbol_track[temp_row['Symbol']].get('Bought'):
                        symbol_track[temp_row['Symbol']]['Bought'] += temp_row['FillSize'] if temp_row['Side'] == 'b' else 0
                    else:
                        symbol_track[temp_row['Symbol']]['Bought'] = temp_row['FillSize'] if temp_row['Side'] == 'b' else 0
                else:
                    symbol_track[temp_row['Symbol']] = {'Bought': temp_row['FillSize'] if temp_row['Side'] == 'b' else 0}
                temp_row['SymbolBought'] = symbol_track[temp_row['Symbol']]['Bought']
                # SymbolSold
                if temp_row['Symbol'] in symbol_track:
                    if symbol_track[temp_row['Symbol']].get('Sold'):
                        symbol_track[temp_row['Symbol']]['Sold'] += temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0
                    else:
                        symbol_track[temp_row['Symbol']]['Sold'] = temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0
                else:
                    symbol_track[temp_row['Symbol']] = {'Bought': temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0}
                temp_row['SymbolSold'] = symbol_track[temp_row['Symbol']]['Sold']
                # SymbolPosition
                temp_row['SymbolPosition'] = temp_row['SymbolBought'] - temp_row['SymbolSold']
                # SymbolNotional
                temp_row['SymbolNotional'] = temp_row['FillSize'] * temp_row['FillPrice']
                # ExchangeBought
                if temp_row['FillExchange'] in exchange_track:
                    if exchange_track[temp_row['FillExchange']].get('Bought'):
                        exchange_track[temp_row['FillExchange']]['Bought'] += temp_row['FillSize'] if temp_row['Side'] == 'b' else 0
                    else:
                        exchange_track[temp_row['FillExchange']]['Bought'] = temp_row['FillSize'] if temp_row['Side'] == 'b' else 0
                else:
                    exchange_track[temp_row['FillExchange']] = {'Bought': temp_row['FillSize'] if temp_row['Side'] == 'b' else 0}
                temp_row['ExchangeBought'] = exchange_track[temp_row['FillExchange']]['Bought']
                # ExchangeSold
                if temp_row['FillExchange'] in exchange_track:
                    if exchange_track[temp_row['FillExchange']].get('Sold'):
                        exchange_track[temp_row['FillExchange']]['Sold'] += temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0
                    else:
                        exchange_track[temp_row['FillExchange']]['Sold'] = temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0
                else:
                    exchange_track[temp_row['FillExchange']] = {'Sold': temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0}
                temp_row['ExchangeSold'] = exchange_track[temp_row['FillExchange']]['Sold']
                # TotalBought
                total_track['Bought'] += temp_row['FillSize'] if temp_row['Side'] == 'b' else 0
                temp_row['TotalBought'] = total_track['Bought']
                # TotalSold
                total_track['Sold'] += temp_row['FillSize'] if temp_row['Side'] in ['t', 's'] else 0
                temp_row['TotalSold'] = total_track['Sold']
                # TotalBoughtNotional
                total_track['BoughtNotional'] += temp_row['SymbolNotional'] if temp_row['Side'] == 'b' else 0
                temp_row['TotalBoughtNotional'] = total_track['BoughtNotional']
                # TotalSoldNotional
                total_track['SoldNotional'] += temp_row['SymbolNotional'] if temp_row['Side'] in ['t', 's'] else 0
                temp_row['TotalSoldNotional'] = total_track['SoldNotional']

                # now write the row to the output file
                trade_writer.writerow(temp_row)
                count += 1
                # trying to think of a better way to calculating median instead of storing all values (is it possible?)
                fill_size_list.append(temp_row['FillSize'])
        try:
            _print_summary(count, symbol_track, exchange_track, total_track, fill_size_list)
        except Exception, e:
            print('cannot print summary. Error: %s' % e)
    except IOError, e:
        print('cannot load csv file. Error: %s' % e)
    except KeyError, e:
        print('dictionary does not have such key. Error: %s' % e)
    except TypeError, e:
        print('field in row might not have the right type for operation or . Error: %s' % e)
    except ValueError, e:
        print('row may contain fields that are not specified in field names. Error: %s' % e)
    except Exception, e:
        print('parsing error. Error: %s' % e)


if __name__ == '__main__':
    # grab input and create output with name
    parser = argparse.ArgumentParser(description=('given imput csv, \
                                                   enhance the fields and write to the output with additional columns.'))
    parser.add_argument('--inputFile', dest='inputfile', help='Path to input file to be parsed')
    parser.add_argument('--outputFile', dest='outputfile', help='Output of enriched csv file')
    args = parser.parse_args()
    calcTradeStats(args.inputfile, args.outputfile)
