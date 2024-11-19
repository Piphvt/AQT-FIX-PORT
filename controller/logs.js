const { connection } = require('../database');

exports.getLogs = (req, res) => {
  connection.query('SELECT * FROM `logs`',
    function (err, results, fields) {
      res.json(results);
    }
  );
}

exports.getLogsByType = (req, res) => {
  const type = req.params.no;
  connection.query('SELECT * FROM `logs` WHERE `type` = ?',
    [type], function (err, results) {
      res.json(results);
    }
  );
}

exports.getLog = (req, res) => {
  const no = req.params.no;
  connection.query('SELECT * FROM `logs` WHERE `no` = ?',
    [no], function (err, results) {
      res.json(results);
    }
  );
}

exports.addLogs = (req, res) => {
  try {
    const { stock_detail_id, stock_id, transaction_id, customer_id, set_id, emp_id, form_id, type, action, detail, emp_name, emp_email, picture,time } = req.body;
    const logData = {
      stock_detail_id,
      stock_id,
      transaction_id,
      customer_id,
      set_id,
      emp_id,
      form_id,
      type,
      action,
      detail,
      emp_name,
      emp_email,
      picture,
      time,
    }
    connection.query('INSERT INTO `logs` SET ?',
      logData, function (err, results) {
        res.json(results);
      }
    );

  } catch (error) {
    console.log("Add Log Error", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
}