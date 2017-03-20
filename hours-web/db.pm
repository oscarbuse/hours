package db;

require Exporter;
@ISA = qw(Exporter);
#@EXPORT = qw($hostname $owner $master $server $port $username $password $dbh);
@EXPORT = qw($dbh);

# initialize package globals, first exported ones
$hostname = "localhost";
$owner = "oscar\@all-stars.nl";
$master = "oscar\@all-stars.nl";
$database = "accounting";		# Name of the MySQL database
$server = "172.18.0.2";
$port = "3306";			# Port on which MySQL receives input
$username = "uren";		# Username for MySQL login
$password = "registratie";	# Password for MySQL login

# connect with database
$dbh = DBI->connect("DBI:mysql:$database:$server:$port",$username,$password);
die "Can not connect with database:", $DBI::errstr unless $dbh;
