from cgitb import html
from moon.model.wallet import AssetsWallet

def convert_assets_wallet_to_html(aw: AssetsWallet) -> str:
  html = """
  <html>
    <head>
      <style>
        #assets {{
          font-family: Arial, Helvetica, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }}

        #assets td, #assets th {{
          border: 1px solid #ddd;
          padding: 8px;
        }}

        #assets tr:nth-child(even){{background-color: #f2f2f2;}}

        #assets tr:hover {{background-color: #ddd;}}

        #assets th {{
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: left;
          background-color: #0066ff;
          color: white;
        }}
      </style>
    </head>
    <body>
      <table id="assets">
        <thead>
          <tr>
            <th>Asset</th>
            <th>Quantité</th>
            <th>PRU</th>
            <th>PRT</th>
          </tr>
        </thead>
        <tbody>
          {}
        </tbody>
      </table>
    </body>
  </html>
  """
  line = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>"
  res = ""
  for asset, data in aw.items():
    res += line.format(asset, round(data.qty,2), round(data.pru,2) , round(data.qty*data.pru,2))
  return html.format(res)
  