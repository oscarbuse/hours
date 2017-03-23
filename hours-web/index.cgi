#!/usr/bin/perl -w
# -----------------------------------------------------------------
# index.cgi
# puts/edits/deletes hours-info in table hours, db accounting
# -----------------------------------------------------------------
# Inititalisatie
# -----------------------------------------------------------------
use strict "vars";
use CGI;
use DBI;
use Date::Calc qw(Delta_Days);
use DateTime::Format::Strptime;
use POSIX;
# global vars and functions
use lib '../libs';
use hours;
use db;

my $CGI = new CGI();
# send the appropriate MIME-header
print $CGI->header("text/html");

my $debug = 0;

# -----------------------------------------------------------------
# Hoofdprogramma
# -----------------------------------------------------------------
# Action -> subroutine mapping
my %ACTIONMAP = (	"Menu"                  => "ShowMenu",
			"SHOW_COLS"		=> "ShowCols",
			"SHOW_SELECTION"	=> "ShowSelection",
			"Add_hours"		=> "ShowForm",
                        "COMMIT_UPLOAD"		=> "CommitUpload",
                        "DO_EDIT"		=> "DoEdit",
                        "COMMIT_EDIT"		=> "CommitEdit",
                        "Delete_hours"		=> "ShowDeleteList",
                        "COMMIT_DELETE"		=> "CommitDelete",
                 );

my $action = $CGI->param('action') || "Menu";

if (! defined $ACTIONMAP{$action})
{
  ShowError("Onbekende actie...<BR>\n",1,0,0,$dbh);
} else {
  &{$ACTIONMAP{$action}};
}
# -----------------------------------------------------------------
# Subroutines
# -----------------------------------------------------------------
sub ShowMenu()
{
  PrintHead("Uren administratie");
print <<EOF;
<center><h3>Uren administratie</h3></center>
<TABLE ALIGN=CENTER BORDER=1>
<TR><TD>
<table border=0 cellpadding=0>
<FORM method="POST" action="index.cgi">
<tr><td colspan=4><h3>Selecteer om weer te geven (x = alles):</h3></td></tr>
EOF
  for my $col (@cols) {
    if ("$col" eq "customer") {
      makeselect($col,\@customers,"select");
    } elsif  ("$col" eq "year") {
      makeselect($col,\@years,"show");
    } elsif  ("$col" eq "month") {
      makeselect($col,\@months,"select");
    } elsif  ("$col" eq "day") {
      makeselect($col,\@days,"select");
    } elsif  ("$col" eq "status") {
      makeselect($col,\@status,"select");
    } elsif  ("$col" eq "billed") {
      makeselect($col,\@billed,"select");
    } elsif  ("$col" eq "description") {
      makeselect($col,\@description,"select");
    } elsif  ("$col" eq "begin") {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1] value=x>hh:mm</td></tr>";
    } elsif  ("$col" eq "end") {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1] value=x>hh:mm</td></tr>";
    } elsif  ("$col" eq "work") {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1] value=x></td></tr>";
    } elsif  ("$col" eq "hours") {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1] value=x>";
    } elsif  ("$col" eq "minutes") {
      print " $colnames{$col}[0] $colnames{$col}[1] value=x></td></tr>";
    } elsif  ("$col" eq "km") {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1]>";
    } elsif  ("$col" eq "kmvoor") {
      print " $colnames{$col}[0] $colnames{$col}[1]> ";
    } elsif  ("$col" eq "kmna") {
      print "$colnames{$col}[0] $colnames{$col}[1]></td></tr>";
    } else {
      print "<tr><td>$colnames{$col}[0]</td><td>$colnames{$col}[1]></td></tr>";
    }
  }
print <<EOF;
<tr><td colspan=4><INPUT TYPE=SUBMIT VALUE=Show></td></tr>
<input type=hidden name=action value=SHOW_COLS>
</form></table>
</TD></TR>

<TR><TD>
<table>
<tr><td>
EOF
  choices();
  print <<EOF;
</td></tr>
</table>
</td></tr>

</table>
EOF
PrintTail();
} # end ShowMenu

sub ShowCols()
{
  PrintHead("Uren administratie");
  print "<h2>Overzicht Werkzaamheden</h2>\n";
  my $head = "<FORM method=\"POST\" action=\"index.cgi\"><table border=1><tr><td>&nbsp;</td>";
  my $select = "id";
  my $where = "";
  $head .= "<td>Del</td>";
  for my $col (@cols) {
    $colvalue{$col} = $CGI->param("$col");
    if ("$colvalue{$col}" ne "") {
      $head .= "<td>$colnames{$col}[0]</td>";
      $select .= ",${col}";
      if  ("$colvalue{$col}" ne "x") {
        if ("$where" eq "") {
          if  ("$col" eq "customer" || "$col" eq "month" || "$col" eq "status" || "$col" eq "billed" || "$col" eq "description") {
            $where = "WHERE $col = \"$colvalue{$col}\"";
          } else {
            $where = "WHERE $col LIKE \"%$colvalue{$col}%\"";
          }
        } else {
          if  ("$col" eq "customer" || "$col" eq "month" || "$col" eq "status" || "$col" eq "billed" || "$col" eq "description") {
            $where .= " AND $col = \"$colvalue{$col}\"";
          } else {
            $where .= " AND $col LIKE \"%$colvalue{$col}%\"";
          }
        }
      }
    }
  }
  $head .= "</tr>\n";

  my $row = "";
  my $sql = "SELECT $select FROM hours $where ORDER BY year , month, day , begin, customer";
  print "sql: $sql<br>\n" if ($debug);
  my $sth = ExecSqlQuery($dbh,$sql);
  my @ids;
  my $reccount = 0;
  my $hourscount = 0;
  my $minutescount = 0;
  my $kmcount = 0;
  if ($sth->rows) {
    while (my @arr = $sth->fetchrow) {
      $reccount++;
      $row .= "<tr>";
      my $array_count = 0;
      my @select = split /,/, $select;
      shift @select; # skip id
      my $id = shift @arr;
      push @ids, $id;
      $row .= "<td><input type=\"radio\" name=\"radio_$id\" value=1></td>";
      for my $col (@select) {
        if ("$colvalue{$col}" eq "" || "$colvalue{$col}" eq "0") {
          $row .= "<td>-</td>";
        } else {
          $hourscount += $arr[${array_count}] if ("$col" eq "hours");
          $minutescount += $arr[${array_count}] if ("$col" eq "minutes");
          $kmcount += $arr[${array_count}] if ("$col" eq "km");
          if ("$col" eq "customer") {
            if (! defined($arr[${array_count}])) {
	      $row .= "<td><a href=index.cgi?action=COMMIT_DELETE&id=$id><font color=\"red\">X</font></a></td>\n";
              $row .= "<td><A HREF=index.cgi?action=DO_EDIT&id=$id>-</A></td>";
            } elsif ("$arr[${array_count}]" eq "") {
	      $row .= "<td><a href=index.cgi?action=COMMIT_DELETE&id=$id><font color=\"red\">X</font></a></td>\n";
              $row .= "<td><A HREF=index.cgi?action=DO_EDIT&id=$id>-</A></td>";
            } else {
	      $row .= "<td><a href=index.cgi?action=COMMIT_DELETE&id=$id><font color=\"red\">X</font></a></td>\n";
              $row .= "<td><A HREF=index.cgi?action=DO_EDIT&id=$id>$arr[${array_count}]</A></td>";
            }
          } elsif ("$col" eq "month") {
            $row .= "<td>$month{$arr[${array_count}]}</td>";
          } else {
            $row .= "<td>$arr[${array_count}]</td>";
          }
        }
        ${array_count}++;
      }
      $row .= "</tr>\n";
    }
  }
  my $tail = "";
  $tail .= "</table>\n";
  #$tail .= ($reccount == 1) ? "&nbsp;&nbsp;$reccount row in set\n" : "&nbsp;&nbsp;$reccount rows in set\n";
  my $minutesrest = 0;
  if ($minutescount >= 60) {
    $minutesrest = $minutescount % 60;
    $hourscount += floor($minutescount/60);
  } else {
    $minutesrest = $minutescount;
  }
  $tail .= "$hourscount uren en $minutesrest minuten\n<br>";
  $tail .= "$kmcount autokilometers\n";
  $tail .= 
  my $htmldata = "$head" . "$row" . "$tail";
  print "${htmldata}<br>\n";
  print "<input type=submit name=show value=Show>\n";
  print "<input type=submit name=hide value=Hide>\n";
  print "<input type=hidden name=action value=SHOW_SELECTION>\n";
  print "<input type=hidden name=selection value=\"$select\">\n";
  print "<input type=hidden name=ids value=\"@ids\">\n";
  print "<input type=hidden name=sql value=\'$sql\'>\n";
  print "</FORM>\n";
  choices();
  PrintTail();
} # end ShowCols

sub ShowSelection()
{
  PrintHead("Uren administratie");
  print "<h2>Overzicht werkzaamheden:</h2>\n";
  my $head = "<FORM method=\"POST\" action=\"index.cgi\"><table border=1><tr><td>Filter</td>";
  my $select = $CGI->param("selection");
  my $oldquery = $CGI->param("sql");
  my $show = $CGI->param("show") || "";
  if ("$show" eq "Show") {
    $show = 1;
  } else {
    $show = 0;
  }
  my @selects = split /,/, $select;
  # shift id
  shift @selects;
  for my $col (@selects) {
    $head .= "<td>$colnames{$col}[0]</td>";
  }
  $head .= "</tr>\n";
  my $ids = $CGI->param("ids");
  $ids =~ s/^ //;
  my $row = "";
  my @ids = split / /, $ids;
  # create sql-query. get all filtered id's
  my $where = "WHERE id in (";
  my @new_ids = "";
  my $choice = 0;
  for my $id (@ids) {
    if ($show) {
      if (defined $CGI->param("radio_$id")) {
        $where .= "${id},";
        $choice = 1;
        push @new_ids, $id;
      }
    } else {
      if (! defined($CGI->param("radio_$id"))) {
        $where .= "${id},";
        $choice = 1;
        push @new_ids, $id;
      }
    }
  }
  @ids = @new_ids if ($choice);;
  $where =~ s/^\,/\)/;
  $where =~ s/\,$/\)/;
  my $sql = "";
  if (! $choice) {
    $sql = $oldquery;
  } else {
    $sql = "SELECT $select FROM hours $where ORDER BY customer";
  }
  print "sql: $sql<br>\n" if ($debug);
  my $sth = ExecSqlQuery($dbh,$sql);
  my $reccount = 0;
  my $hourscount = 0;
  if ($sth->rows) {
    while (my @arr = $sth->fetchrow) {
      $reccount++;
      $row .= "<tr>";
      my $array_count = 0;
      my @select = split /,/, $select;
      shift @select; # skip id
      my $id = shift @arr;
      $row .= "<td><input type=\"radio\" name=\"radio_$id\" value=1></td>";
      for my $col (@select) {
        $hourscount += $arr[${array_count}] if ("$col" eq "hours");
        if ("$col" eq "customer") {
          $row .= "<td><A HREF=index.cgi?action=DO_EDIT&id=$id>$arr[${array_count}]</A></td>";
        } else {
          $row .= "<td>$arr[${array_count}]</td>";
        }
        ${array_count}++;
      }
      $row .= "</tr>\n";
    }
  }
  my $tail = "";
  $tail .= "</table>\n";
  #$tail .= ($reccount == 1) ? "&nbsp;&nbsp;$reccount row in set\n" : "&nbsp;&nbsp;$reccount rows in set\n";
  $tail .= "$hourscount uren\n";
  $tail .= 
  my $htmldata = "$head" . "$row" . "$tail";
  print "${htmldata}<br>\n";
  print "<input type=submit name=show value=Show>\n";
  print "<input type=submit name=hide value=Hide>\n";
  print "<input type=hidden name=action value=SHOW_SELECTION>\n";
  print "<input type=hidden name=selection value=\"$select\">\n";
  print "<input type=hidden name=ids value=\"@ids\">\n";
  print "<input type=hidden name=sql value=\'$sql\'>\n";
  print "</FORM>\n";
  PrintTail();
} # end ShowSelection

sub ShowForm()
{
  PrintHead("Uren administratie");
  # Create the form
  print <<EOF;
<form method="POST" action="index.cgi">
<h2>Voeg werkzaamheden toe</h2>
<table border=0>
EOF
  for my $col (@cols) {
    if ("$col" eq "customer") {
      makeselect($col,\@customers,"add");
    } elsif  ("$col" eq "year") {
      makeselect($col,\@years,"add");
    } elsif  ("$col" eq "month") {
      makeselect($col,\@months,"add");
    } elsif  ("$col" eq "day") {
      makeselect($col,\@days,"add");
    } elsif ("$col" eq "status") {
      makeselect($col,\@status,"add");
    } elsif ("$col" eq "billed") {
      makeselect($col,\@billed,"add");
    } elsif ("$col" eq "description") {
      makeselect($col,\@description,"add");
    } elsif ("$col" eq "work") {
      print "<tr><td>$colnames{$col}[0]:</td><td><textarea cols=\"70\" rows=\"16\" name=work></textarea></td></tr>\n";
    } elsif ("$col" eq "begin") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"09:00\"> hh-mm</td></tr>\n";
    } elsif ("$col" eq "end") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"17:00\"> hh-mm</td></tr>\n";
    } elsif  ("$col" eq "hours") {
      print "<tr><td>$colnames{$col}[0]:</td><td>$colnames{$col}[1]>";
    } elsif  ("$col" eq "minutes") {
      print " $colnames{$col}[0]: $colnames{$col}[1]></td></tr>";
    } elsif  ("$col" eq "km") {
      print "<tr><td>$colnames{$col}[0]:</td><td>$colnames{$col}[1]>";
    } elsif  ("$col" eq "kmvoor") {
      print " $colnames{$col}[0]: $colnames{$col}[1]> ";
    } elsif  ("$col" eq "kmna") {
      print "$colnames{$col}[0]: $colnames{$col}[1]></td></tr>";

    } else {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1]></td></tr>\n";
    }
  }
  print <<EOF;
<tr><td><input type=submit value="Add"></td><td>&nbsp;</td></tr>
</table>
<input type=hidden name=action value="COMMIT_UPLOAD">
</Form>
EOF
  # Finish the HTML
  PrintTail();
} # end ShowForm

sub CommitUpload()
{
  PrintHead("Uren administratie");
  for my $col (@cols) {
    $colvalue{$col} =  $dbh->quote($CGI->param("$col")) || "-";
    $colvalue{$col} = "'-'" if ("$colvalue{$col}" eq "''");
    $colvalue{$col} = "NULL" if ("$colvalue{$col}" eq "'-'" && "$col" eq "customer");
  } 
  # calculate hours/minutes when empty
  if ($colvalue{"hours"} = '-' && $colvalue{"minutes"} = '-') {
    my $fmt = '%H:%M';
    my $parser = DateTime::Format::Strptime->new(pattern => $fmt);
    my $dt1 = $parser->parse_datetime($colvalue{"begin"}) or die;
    my $dt2 = $parser->parse_datetime($colvalue{"end"}) or die;
    my $diff = $dt2 - $dt1;
    $colvalue{"hours"} = $diff->hours;
    $colvalue{"minutes"} = $diff->minutes;
  }

  # put data in table hours
  # create query
  my $sql = "INSERT INTO hours (";
  for my $col (@cols) {
    if ("$col" eq "work") {
      $sql .= "${col}) ";
    } else {
      $sql .= "$col, ";
    }
  }
  $sql .= "VALUES (";
  for my $col (@cols) {
    # next if ("$col" eq "beslisdatum");
    if ("$col" eq "work") {
      $sql .= "$colvalue{$col})";
    } else {
      $sql .= "$colvalue{$col}, ";
    }
  }
  print "sql:  $sql<br>\n" if ($debug);
  print "dbh:  $dbh<br>\n" if ($debug);

  # ------------------------------------------------------------
  # insert into table hours
  # ------------------------------------------------------------
  my $sth = ExecSqlQuery($dbh,$sql);
  $sth->finish;

  print "<H3>New hours added.</H3>\n";
  PrintTail();
} # end CommitUpload

sub DoEdit()
{
  my $id = $CGI->param("id") || "";
  PrintHead("Edit hours-info for host");
  my $sql = "SELECT customer,year,month,day,begin,end,hours,minutes,km,kmvoor,kmna,status,billed,invoice,description,work FROM hours WHERE id = $id";
  my $sth = ExecSqlQuery($dbh,$sql);
  my @result = "";
  if (! (@result = $sth->fetchrow)) {
    ShowError("Kan hours-info om te wijzigen niet vinden...",1,0,$sth,$dbh);
  }
  $sth->finish;
  $dbh->disconnect;
  # Create the form
  print <<EOF;
<form method="POST" action="index.cgi">
<h2>Edit hours-info for host</h2>
<table border=0>
EOF
  my $count = 0;
  for my $col (@cols) {
    if ("$col" eq "customer") {
      editselect($col,\@customers,\@result,$count);
    } elsif ("$col" eq "year") {
      editselect($col,\@years,\@result,$count);
    } elsif ("$col" eq "month") {
      editselect($col,\@months,\@result,$count);
    } elsif ("$col" eq "day") {
      editselect($col,\@days,\@result,$count);
    } elsif ("$col" eq "status") {
      editselect($col,\@status,\@result,$count);
    } elsif ("$col" eq "billed") {
      editselect($col,\@billed,\@result,$count);
    } elsif ("$col" eq "description") {
      editselect($col,\@description,\@result,$count);
    } elsif ("$col" eq "work") {
      print "<tr><td>$colnames{$col}[0]:</td><td><textarea cols=\"70\" rows=\"16\" name=work>$result[$count]</textarea></td></tr>\n";
    } elsif ("$col" eq "begin") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"$result[$count]\">hh:mm</td></tr>\n";
    } elsif ("$col" eq "end") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"$result[$count]\">hh:mm</td></tr>\n";
    } elsif  ("$col" eq "hours") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"$result[$count]\"> \n";
    } elsif  ("$col" eq "minutes") {
      print "$colnames{$col}[0]: $colnames{$col}[1] value=\"$result[$count]\"></td></tr>\n";
    } elsif ("$col" eq "km") {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"$result[$count]\"> \n";
    } elsif ("$col" eq "kmvoor") {
      print " $colnames{$col}[0]: $colnames{$col}[1] value=\"$result[$count]\"> - ";
    } elsif ("$col" eq "kmna") {
      print "$colnames{$col}[0]: $colnames{$col}[1] value=\"$result[$count]\"></td></tr>\n";
    } else {
      print "<tr><td>$colnames{$col}[0]:</td><td align=left>$colnames{$col}[1] value=\"$result[$count]\"></td></tr>\n";
    }
    $count++;
  }
  print <<EOF;
<tr><td><input type=submit value="Edit"></td><td>&nbsp;</td></tr>
</table>
<input type=hidden name=action value="COMMIT_EDIT">
<input type=hidden name=id value="$id">
</Form>
EOF
  PrintTail();
} # end DoEdit

sub CommitEdit()
{
  my $id = $CGI->param("id") || "";
  PrintHead("Commit edit hours-info voor host");
  for my $col (@cols) {
    $colvalue{$col} =  $dbh->quote($CGI->param("$col")) || "-";
    $colvalue{$col} = "'-'" if ("$colvalue{$col}" eq "''");
    $colvalue{$col} = "NULL" if ("$colvalue{$col}" eq "'-'" && "$col" eq "customer");
  }

  # create query
  my $sql = "UPDATE hours SET ";
  for my $col (@cols) {
    if ("$col" eq "work") {
      $sql .= "$col = $colvalue{$col} ";
    } else {
      $sql .= "$col = $colvalue{$col}, ";
    }
  }
  $sql .= "WHERE id = \"$id\" ";
  print "sql: $sql<br>\n" if ($debug);
  # ------------------------------------------------------------
  # insert into table demos
  # ------------------------------------------------------------
  my $sth = ExecSqlQuery($dbh,$sql);
  $sth->finish;
  $dbh->disconnect;

  print "<H3>Hours-info for host is changed</h3>\n";
  PrintTail();
} # end CommitEdit

sub ShowDeleteList()
{
  PrintHead("Delete hours");
  my $sql = "SELECT id, customer, year, month, day, begin, end, status, description, work FROM hours ORDER BY customer";
  my $sth = ExecSqlQuery($dbh,$sql);
  # Create delete list
  if ($sth->rows) {
    print "<h2>Kies om te verwijderen:</h2>\n";
    print "<table border=1><tr><td>Customer</td><td>datum - tijd</td><td>Status</td><td>Description</td><td>Work</td></tr>\n";
    while (my @arr = $sth->fetchrow) {
      my ($id, $customer, $year, $month, $day, $begin, $end, $status, $description, $work) = @arr;
      print "<tr><td><a href=index.cgi?action=COMMIT_DELETE&id=$id>$customer</a></td><td>$day/$month/$year - $begin:$end</td><td>$status</td><td>$description</td><td>$work</td></tr>\n";
    }
    print "</table>\n";
  }
  $sth->finish;
  $dbh->disconnect;
  PrintTail();
} # end sub ShowDeleteList

sub CommitDelete()
{
  PrintHead("Commit delete hours");
  my $id = $CGI->param("id") || "";

  my $sql = "DELETE FROM hours WHERE id = \"$id\"";
  print "sql: $sql<br>\n" if ($debug);
  my $sth = ExecSqlQuery($dbh,$sql);

  $sth->finish;

  print "<H3>hours deleted!</h3>\n";
  PrintTail();
  $dbh->disconnect;
} # end CommitDelete
