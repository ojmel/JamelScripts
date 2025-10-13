# import time
#
# import numpy as np
# import pandas as pd
# from pandasgui import show
# import yfinance as yf
#
# tickers = pd.read_csv(r"C:\Users\jamel\Downloads\ExportTable (2).csv", index_col='Symbol')
# tickers['diff_to_low'] = ((tickers['Last'] - tickers['52 Week Low']) / tickers['52 Week Low']) * 100
# tickers=tickers.sort_values(by='Percent Average Call Volume',ascending=False).query("diff_to_low<50 and Sector not in ['--','Financials','Real Estate']")
# def get_call_options(ticker) -> pd.DataFrame:
#     time.sleep(1)
#     stock = yf.Ticker(ticker)
#     # Fetch options expiration dates
#     expirations = stock.options
#     print("Available Expiration Dates:", expirations)
#     if expirations:
#         expiration_date = expirations[1]  # Example: First expiration date
#         options_chain = stock.option_chain(expiration_date)
#
#         # Separate calls and puts
#         return options_chain.calls
#
# for index,ticker in enumerate(tickers.index[6:]):
#     calls=get_call_options(ticker)
#     differences = np.abs(calls['strike'] - tickers.loc[ticker,'Last'])
#     nearest_indices = differences.argsort()[:2]
#     nearest_calls = calls.iloc[nearest_indices]
#     nearest_calls['price']=tickers.loc[ticker,'Last']
#     nearest_calls['Sector']=tickers.loc[ticker,'Sector']
#     if (nearest_calls['lastPrice']<0.3).any():
#         show(nearest_calls[['contractSymbol','strike','bid','ask','price','Sector','lastPrice']])
#     print(index)
from dnslib import DNSRecord, QTYPE, RR, A, DNSHeader
import socket
import socketserver
# Get the local IP address
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
# DNS server configuration
print(local_ip)
DOMAIN_TO_IP = {
   'a.com.': '10.0.0.34',
   'jamelly.welly.': local_ip,
}
class DNSHandler(socketserver.BaseRequestHandler):
   def handle(self):
       data = self.request[0].strip()
       socket = self.request[1]
       try:
           request = DNSRecord.parse(data)
           print(f"Received request for: {str(request.q.qname)}")
           # Create a DNS response with the same ID and the appropriate flags
           reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
           qname = str(request.q.qname)
           qtype = QTYPE[request.q.qtype]
           if qname in DOMAIN_TO_IP:
               reply.add_answer(RR(qname, QTYPE.A, rdata=A(DOMAIN_TO_IP[qname])))
               print(f"Resolved {qname} to {DOMAIN_TO_IP[qname]}")
           else:
               print(f"No record found for {qname}")
           socket.sendto(reply.pack(), self.client_address)
       except Exception as e:
           print(f"Error handling request: {e}")
if __name__ == "__main__":
   server = socketserver.UDPServer((local_ip, 53), DNSHandler)
   print("DNS Server is running...")
   server.serve_forever()
