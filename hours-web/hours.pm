package hours;

require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(@cols @years @months %month @days %colnames %colvalue %customer_full @customers @status @billed @description &makeselect &editselect &PrintHead &PrintTail &ShowError &ExecSqlQuery &get_year &get_month &get_day &choices);

@cols = qw(customer year month day begin end hours minutes km kmvoor kmna status billed invoice description work);
@years = qw(2011 2012 2013 2014 2015 2016 2017);
@months = qw(01 02 03 04 05 06 07 08 09 10 11 12);
%month = (
  '01'	=> 'januari',
  '02'	=> 'februari',
  '03'	=> 'maart',
  '04'	=> 'april',
  '05'	=> 'mei',
  '06'	=> 'juni',
  '07'	=> 'juli',
  '08'	=> 'augustus',
  '09'	=> 'september',
  '10'	=> 'oktober',
  '11'	=> 'november',
  '12'	=> 'december',
);

@days = ("01","02","03","04","05","06","07","08","09",10 .. 31);

#
# functions
#
sub choices {
  my %actions = (
    'Add_hours' => 'Voeg toe',
    'Delete_hours' => 'Verwijder',
  );

  print "<form method=\"POST\" action=\"index.cgi\">\n";
  print "<table><tr><td><select name=action>\n";
  for my $action ( keys %actions )
  {
    if ($action eq "Add_hours")
    {
      print "<option selected value=\"$action\">$actions{$action}\n";
    } else
    {
      print "<option value=\"$action\">$actions{$action}\n";
    }
  }
  print "</select>\n";
  print "<input type=submit value=Go></td></tr></table>\n";
  print "</form>\n";
}

sub get_day() {
  my ($currentday) = (localtime)[3];
  if ($currentday < 10) {
    $currentday = "0" . $currentday;
  }
  return $currentday;
}
sub get_month() {
  my ($currentmonth) = (localtime)[4];
  $currentmonth++;
  if ($currentmonth < 10) {
    $currentmonth = "0" . $currentmonth;
  }
  return $currentmonth;
}

sub get_year() {
  my ($currentyear) = (localtime)[5];
  $currentyear = $currentyear + 1900;
  return $currentyear;
}



sub makeselect($$$;)
{
  my $col = shift;
  my $col_r = shift;
  my @col_r = @$col_r;
  my $tag = shift;

  print "<tr><td>$colnames{$col}[0]:</td><td><SELECT name=$col>\n";
  if (($col eq "customer") || ($col eq "month") || ($col eq "day") || ($col eq "status") || ($col eq "description")) {
    print "<option value=\"\">\n";
    print "<option selected value=x>x\n";
  } else {
    print "<option selected value=\"\">\n";
    print "<option value=x>x\n";
  }
  for my $action (@col_r) {
    if ($tag eq "add") {
      if ($col eq "month") {
        my $cur_month = get_month();
        if ($cur_month eq $action) {
          print "<option selected value=\"$action\">$month{$action}\n";
        } else {
          print "<option value=\"$action\">$month{$action}\n";
        }
      } elsif ($col eq "day") {
        my $cur_day = get_day();
        if ($cur_day eq $action) {
          print "<option selected value=\"$action\">$action\n";
        } else {
          print "<option value=\"$action\">$action\n";
        }
      } elsif ($col eq "year") {
        my $cur_year = get_year();
        if ($cur_year eq $action) {
          print "<option selected value=\"$action\">$action\n";
        } else {
          print "<option value=\"$action\">$action\n";
        }
      } else {
        print "<option value=\"$action\">$action\n";
      }
    } else {
      if ($col eq "month") {
        my $cur_month = get_month();
        if ($cur_month eq $action) {
          print "<option selected value=\"$action\">$month{$action}\n";
        } else {
          print "<option value=\"$action\">$month{$action}\n";
        }
      } elsif ($col eq "year") {
        my $cur_year = get_year();
        if ($cur_year eq $action) {
          print "<option selected value=\"$action\">$action\n";
        } else {
          print "<option value=\"$action\">$action\n";
        }
      } else {
        print "<option value=\"$action\">$action\n";
      }
    }
  }
  print "</SELECT></td></tr>\n";
}
sub editselect($$$$;)
{
  my $col = shift;
  my $col_r = shift;
  my @col_r = @$col_r;
  my $result = shift;
  my @result = @$result;
  my $count = shift;
  print "<tr><td>$colnames{$col}[0]:</td><td><SELECT name=$col>\n";
  if ("$result[$count]" eq "-" || "$result[$count]" eq "") {
    print "<option selected value=\"-\">-\n";
    for my $action (@$col_r) {
      print "<option value=\"$action\">$action\n";
    }
  } else {
    for my $action (@col_r) {
      if ($action eq $result[$count]) {
        print "<option selected value=\"$action\">$action\n";
      } else {
        print "<option value=\"$action\">$action\n";
      }
    }
  }
  print "</SELECT></td></tr>\n";
}


sub PrintHead($;)
{
  my $title = shift;
  #my $js = shift;
  if ("$title" ne "")
  {
    print <<EOF;
<html><head><title>$title</title>
<meta name="generator" content="VI VI VI: the editor of the beast" />
</head>
<body>
EOF
  }
}

sub PrintTail()
{
  print "<a href=\"index.cgi\">Home</a>\n";
  print "</body></html>\n";
} # end PrintTail

sub ShowError($$$$$) {
  my $errstr1 = shift || "";
  my $contact = shift || 0;
  my $back = shift || 0;
  my $sth = shift || 0;
  my $dbh = shift || 0;
  $sth->finish if ($sth);
  $dbh->disconnect if ($dbh);
  print "<H1>Error</H1>\n";
  print "<H4>$errstr1</H4>";
  if ($contact)
  {
    print "<H4>Neem contact op met de <a href=\"mailto:webmaster\@kwalinux.nl\">webmaster</a> van deze site en vermeld daarbij deze foutmelding</H4>";
  }
  if ($back)
  {
    print "<p>\n";
    print "Druk op de Back (of Vorige) - button in uw browser en ";
    print "probeer het opnieuw.\n";
    print "</p>\n";
  }
  PrintTail();
  exit 1;
}

sub ExecSqlQuery($$) {
  my $dbh = shift;
  my $cmd = shift;
  #print "sql-commando: $cmd<BR>";
  # send the query
  my $sth = $dbh->prepare($cmd);
  ShowError("Fout met database",1,0,0,$dbh) unless $sth;

  # Execute the query
  my $result = $sth->execute;
  ShowError("Fout met database",1,0,$sth,$dbh) unless $result;

  return $sth;
}

%colnames = (
  'customer'  	        => ['Klant',''],
  'year'     		=> ['Jaar',''],
  'month'        	=> ['Maand',''],
  'day'                 => ['Dag',''],
  'begin'               => ['Begin','<input type=text size=5 name=begin'],
  'end'                 => ['Eind','<input type=text size=5 name=end'],
  'hours'               => ['Uren','<input type=text size=5 name=hours'],
  'minutes'             => ['Minutes','<input type=text size=3 name=minutes'],
  'km'            	=> ['Km (auto)','<input type=text size=5 name=km'],
  'kmvoor'      	=> ['Km voor','<input type=text size=7 name=kmvoor'],
  'kmna'      		=> ['Km na','<input type=text size=7 name=kmna'],
  'status'      	=> ['Status',''],
  'billed'      	=> ['Gefactureerd',''],
  'invoice'             => ['Factuur','<input type=text size=30 name=invoice'],
  'description'         => ['Omschrijving',''],
  'work'                => ['Werkzaamheden','<input type=text size=40 name=work'],
);
%colvalue = (
  'customer'         => '',
  'year'             => '',
  'month'            => '',
  'day'              => '',
  'begin'            => '',
  'end'              => '',
  'hours'            => '',
  'minutes'          => '',
  'km'               => '',
  'kmvoor'           => '',
  'kmna'             => '',
  'status'           => '',
  'billed'           => '',
  'invoice'          => '',
  'description'      => '',
  'work'             => '',
);

# customers
@customers = ('Focus online','Water Insight','AT','AT Consultancy','donux','liqit','osgn','isatis','jcr','jef','viafrica','ViafricaZ','kpn','momac','nasc','NICE', 'huiscoach','dijktraining','iteducation','camarate', 'tetraned', 'vijfhart', 'mtv', 'upact', 'roc', 'kwalinux','vu','vu-somalia');
%customer_full = (
  'Focus online'	=> 'Focus online',
  'Water Insight'	=> 'Water Insight',
  'AT'			=> 'AT Computing BV',
  'AT Consultancy'      => 'AT Consultancy BV',
  'donux'		=> 'Donux',
  'ligit'		=> 'LiQiT',
  'osgn'		=> 'Open Source Group Nederland',
  'isatis'		=> 'Isatis',
  'jcr'			=> 'Julius Clinial Research',
  'jef'			=> 'jefvandenputte architectuur',
  'viafrica'    	=> 'Viafrica',
  'ViafricaZ'    	=> 'Viafrica zakelijk',
  'kpn'    		=> 'KPN',
  'momac'    	        => 'Momac',
  'nasc'    	        => 'NASC - Netherlands Academy Support Center',
  'NICE'    	        => 'NICE international',
  'huiscoach'		=> 'Dijk huiscoach',
  'dijktraining'	=> 'Dijk training & coaching',
  'iteducation'		=> 'IT education',
  'camarate'		=> 'camarate ICT',
  'tetraned'		=> 'Tetraned',
  'vijfhart'		=> 'Vijfhart IT-Opleidingen',
  'mtv'			=> 'MTV Networks',
  'upact'		=> 'Upact.nl',
  'roc'			=> 'ROC',
  'kwalinux'		=> 'KwaLinux Trainingen',
  'vu'			=> 'Vrije Universiteit',
  'vu-somalia'		=> 'Vrije Universiteit Project Somalia',
);
# end customers
@status = qw(voorbereiding bezig afgerond onbekend);
@billed = qw(Ja Nee);
@description = (
        'werkzaamheden website',
        'overleg',
        'reizen',
        'inwerken',
        'boekhouding',
        'offerte opstellen',
        'live zetten website',
        'voorbereiden',
        'email afhandeling',
        'training',
        'training volgen',
        'training voorbereiden',
        'presentatie geven',
        'presentatie voorbereiden',
        'bijwonen presentatie / event',
        'ontwikkeling',
        'ontwikkeling cursusmateriaal',
        'studie',
        'overig',
        'sollicitatie',
        'acquisitie',
        'systeembeheer',
        'documentatie',
        'studiewijzer/ppt',
        'maken lesplan',
        'invullen wiki',
        'content verzamelen');
