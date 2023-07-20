<html>
  <head>
    <title>eason's game</title>
    <link rel="stylesheet" href="https://pyscript.net/alpha/pyscript.css" />
    <script defer src="https://pyscript.net/alpha/pyscript.js"></script>
    <py-env>
      - pytest
      - paths:
          - ./src/coin_collect_gam.py
    </py-env>
  </head>
  <body>
    <h1>Update HTML from PYTHON</h1>
    <b> <label id="output"></label></b>
    <py-script>
      from pytest import function
      pyscript.write('output', function())
    </py-script>
  </body>
</html>