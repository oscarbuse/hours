package db;

require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw($dbh);

# initialize package globals, first exported ones
$hostname = "localhost";
$database = "accounting";
$server = "172.18.0.2";
$port = "3306";
$username = "alice";		# Username for MySQL login
$password = "changeme";		# Password for MySQL login

# connect with database
$dbh = DBI->connect("DBI:mysql:$database:$server:$port",$username,$password);
die "Can not connect with database:", $DBI::errstr unless $dbh;
