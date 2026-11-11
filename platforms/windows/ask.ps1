param(
    [string]$Prompt = "Please enter:",
    [string]$Title = "EyeGuard",
    [string]$OutFile = "",
    [int]$Masked = 1,
    [int]$IsConfirm = 0
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$font = New-Object Drawing.Font("Microsoft YaHei UI", 10)

$form = New-Object Windows.Forms.Form
$form.Text = $Title
$form.Size = New-Object Drawing.Size(460, 210)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true
$form.Font = $font

$lbl = New-Object Windows.Forms.Label
$lbl.Text = $Prompt
$lbl.SetBounds(22, 20, 400, 44)
$form.Controls.Add($lbl)

$tb = New-Object Windows.Forms.TextBox
$tb.SetBounds(22, 68, 400, 26)
$tb.Font = New-Object Drawing.Font("Microsoft YaHei UI", 11)
if ($Masked -eq 1) { $tb.UseSystemPasswordChar = $true }
$form.Controls.Add($tb)

if ($IsConfirm -eq 1) {
    $tb2 = New-Object Windows.Forms.TextBox
    $tb2.SetBounds(22, 104, 400, 26)
    $tb2.Font = New-Object Drawing.Font("Microsoft YaHei UI", 11)
    if ($Masked -eq 1) { $tb2.UseSystemPasswordChar = $true }
    $form.Controls.Add($tb2)
}

$ok = New-Object Windows.Forms.Button
$ok.Text = "确定"
$ok.DialogResult = "OK"
$ok.SetBounds(262, 132, 78, 30)
$form.Controls.Add($ok)

$cancel = New-Object Windows.Forms.Button
$cancel.Text = "取消"
$cancel.DialogResult = "Cancel"
$cancel.SetBounds(352, 132, 78, 30)
$form.Controls.Add($cancel)

$form.AcceptButton = $ok
$form.CancelButton = $cancel
$form.Add_Shown({ $tb.Focus() })

$res = $form.ShowDialog()
$value = $tb.Text
if ($IsConfirm -eq 1) { $second = $tb2.Text } else { $second = "" }
$form.Dispose()

if ($res -eq "OK" -and $OutFile -ne "") {
    $payload = $value + "`u{001F}" + $second
    [IO.File]::WriteAllText($OutFile, $payload, (New-Object Text.UTF8Encoding($false)))
}
