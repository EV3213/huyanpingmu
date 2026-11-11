# 护眼管家 · 家长端（EyeGuard Parent App）
# 独立窗口，不依赖 Python 的 GUI 组件；读写同目录的 config.json / state.json
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfgPath = Join-Path $root "config.json"
$statePath = Join-Path $root "state.json"
$TITLE = "护眼管家 · 家长端"

function Read-Json($path, $fallback) {
    try {
        if (Test-Path $path) {
            $raw = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
            if ($raw.Trim() -ne "") { return ($raw | ConvertFrom-Json) }
        }
    } catch { }
    return $fallback
}

function Write-JsonUtf8($path, $obj) {
    $json = $obj | ConvertTo-Json -Depth 6
    [IO.File]::WriteAllText($path, $json, (New-Object Text.UTF8Encoding($false)))
}

function Get-PinHash($salt, $pin) {
    $sha = [Security.Cryptography.SHA256]::Create()
    $bytes = [Text.Encoding]::UTF8.GetBytes("$salt|$pin")
    $h = $sha.ComputeHash($bytes)
    return (($h | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Set-Field($obj, $name, $value) {
    $obj | Add-Member -NotePropertyName $name -NotePropertyValue $value -Force
}

function New-PinDialog($prompt, $confirm) {
    $f = New-Object Windows.Forms.Form
    $f.Text = $TITLE
    $f.Size = New-Object Drawing.Size(460, $(if ($confirm) { 250 } else { 200 }))
    $f.StartPosition = "CenterScreen"
    $f.FormBorderStyle = "FixedDialog"
    $f.MaximizeBox = $false
    $f.MinimizeBox = $false
    $f.TopMost = $true
    $f.Font = New-Object Drawing.Font("Microsoft YaHei UI", 10)

    $l = New-Object Windows.Forms.Label
    $l.Text = $prompt
    $l.SetBounds(22, 18, 400, 40)
    $f.Controls.Add($l)

    $t1 = New-Object Windows.Forms.TextBox
    $t1.UseSystemPasswordChar = $true
    $t1.SetBounds(22, 62, 400, 26)
    $t1.Font = New-Object Drawing.Font("Microsoft YaHei UI", 11)
    $f.Controls.Add($t1)

    $t2 = $null
    if ($confirm) {
        $t2 = New-Object Windows.Forms.TextBox
        $t2.UseSystemPasswordChar = $true
        $t2.SetBounds(22, 100, 400, 26)
        $t2.Font = New-Object Drawing.Font("Microsoft YaHei UI", 11)
        $f.Controls.Add($t2)
    }

    $btnY = if ($confirm) { 148 } else { 106 }

    $ok = New-Object Windows.Forms.Button
    $ok.Text = "确定"
    $ok.DialogResult = "OK"
    $ok.SetBounds(262, $btnY, 78, 30)
    $f.Controls.Add($ok)

    $no = New-Object Windows.Forms.Button
    $no.Text = "取消"
    $no.DialogResult = "Cancel"
    $no.SetBounds(352, $btnY, 78, 30)
    $f.Controls.Add($no)

    $f.AcceptButton = $ok
    $f.CancelButton = $no
    $f.Add_Shown({ $t1.Focus() })

    $res = $f.ShowDialog()
    $v1 = $t1.Text
    $v2 = if ($null -ne $t2) { $t2.Text } else { "" }
    $f.Dispose()

    if ($res -eq "OK") { return @($v1, $v2, $true) }
    return @("", "", $false)
}

function Show-Msg($text) {
    [Windows.Forms.MessageBox]::Show($text, $TITLE) | Out-Null
}

# ---------------- 认证 ----------------
$cfg = Read-Json $cfgPath $null
if ($null -eq $cfg) { $cfg = New-Object PSObject }

$hasPin = $false
if ($cfg.PSObject.Properties.Name -contains "admin_pin_sha256") {
    if ($cfg.admin_pin_sha256 -and "$($cfg.admin_pin_sha256)".Length -gt 0) { $hasPin = $true }
}

if (-not $hasPin) {
    Show-Msg "第一次打开家长端，请先设置家长密码。`n`n设好之后：学习端不能改时长、不能暂停，退出也要这个密码。"
    while ($true) {
        $a = New-PinDialog "设置家长密码（至少 4 位）" $false
        if (-not $a[2]) { exit }
        if ($a[0].Length -lt 4) { Show-Msg "密码至少 4 位"; continue }
        $b = New-PinDialog "再输入一次" $false
        if (-not $b[2]) { exit }
        if ($a[0] -ne $b[0]) { Show-Msg "两次输入不一致，重来"; continue }
        $salt = -join ((48..57) + (97..102) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
        Set-Field $cfg "admin_salt" $salt
        Set-Field $cfg "admin_pin_sha256" (Get-PinHash $salt $a[0])
        Write-JsonUtf8 $cfgPath $cfg
        break
    }
} else {
    $left = 3
    $passed = $false
    while ($left -gt 0) {
        $a = New-PinDialog "请输入家长密码（还可以试 $left 次）" $false
        if (-not $a[2]) { exit }
        if ((Get-PinHash $cfg.admin_salt $a[0]) -eq $cfg.admin_pin_sha256) { $passed = $true; break }
        $left = $left - 1
        if ($left -gt 0) { Show-Msg "密码不对，还可以试 $left 次" }
    }
    if (-not $passed) { exit }
}

# ---------------- 界面 ----------------
$GREEN = [Drawing.ColorTranslator]::FromHtml("#12644A")
$GREY = [Drawing.ColorTranslator]::FromHtml("#6B7772")
$BG = [Drawing.ColorTranslator]::FromHtml("#F4F7F5")

$form = New-Object Windows.Forms.Form
$form.Text = $TITLE
$form.Size = New-Object Drawing.Size(640, 830)
$form.StartPosition = "CenterScreen"
$form.BackColor = $BG
$form.Font = New-Object Drawing.Font("Microsoft YaHei UI", 9.5)
$form.MaximizeBox = $false
$form.FormBorderStyle = "FixedSingle"

$title = New-Object Windows.Forms.Label
$title.Text = "护眼管家 · 家长端"
$title.Font = New-Object Drawing.Font("Microsoft YaHei UI", 17, [Drawing.FontStyle]::Bold)
$title.ForeColor = $GREEN
$title.SetBounds(20, 14, 400, 36)
$form.Controls.Add($title)

$sub = New-Object Windows.Forms.Label
$sub.Text = "学习端已锁定：孩子只能主动休息、看进度，改不了时长、暂停不了、退出要密码。下面改完点保存，约 1 秒自动生效，不用重启。"
$sub.ForeColor = $GREY
$sub.SetBounds(22, 52, 578, 40)
$form.Controls.Add($sub)

function New-Group($caption, $y, $h) {
    $g = New-Object Windows.Forms.GroupBox
    $g.Text = " " + $caption + " "
    $g.ForeColor = $GREEN
    $g.SetBounds(18, $y, 588, $h)
    $form.Controls.Add($g)
    return $g
}

function New-RowLabel($parent, $text, $x, $y, $w) {
    $l = New-Object Windows.Forms.Label
    $l.Text = $text
    $l.ForeColor = [Drawing.Color]::FromArgb(40, 44, 42)
    $l.SetBounds($x, $y, $w, 22)
    $parent.Controls.Add($l)
    return $l
}

function New-Num($parent, $x, $y, $value, $min, $max, $step) {
    $n = New-Object Windows.Forms.NumericUpDown
    $n.Minimum = $min
    $n.Maximum = $max
    $n.Increment = $step
    if ($value -lt $min) { $value = $min }
    if ($value -gt $max) { $value = $max }
    $n.Value = $value
    $n.SetBounds($x, $y, 68, 24)
    $n.Font = New-Object Drawing.Font("Microsoft YaHei UI", 10)
    $n.TextAlign = "Center"
    $parent.Controls.Add($n)
    return $n
}

# --- 学习计划 ---
$gPlan = New-Group "学习计划" 100 226

New-RowLabel $gPlan "每轮专注多久" 14 28 104 | Out-Null
$nInterval = New-Num $gPlan 124 26 ([int]("0" + $cfg.interval_min)) 5 120 5
New-RowLabel $gPlan "分钟" 198 28 36 | Out-Null
$tip1 = New-RowLabel $gPlan "普通软件、工作网页按这个走" 240 28 330 | Out-Null
$tip1.ForeColor = $GREY

New-RowLabel $gPlan "休息多久" 14 62 104 | Out-Null
$nBreak = New-Num $gPlan 124 60 ([int]("0" + $cfg.break_sec)) 5 300 5
New-RowLabel $gPlan "秒" 198 62 36 | Out-Null
$tip2 = New-RowLabel $gPlan "全屏绿植画面 + 语音提醒的时长" 240 62 330 | Out-Null
$tip2.ForeColor = $GREY

New-RowLabel $gPlan "娱乐网页" 14 96 104 | Out-Null
$nEnt = New-Num $gPlan 124 94 ([int]("0" + $cfg.entertainment_min)) 5 120 5
New-RowLabel $gPlan "分钟" 198 96 36 | Out-Null
$tip3 = New-RowLabel $gPlan "B 站、抖音、YouTube 这类" 240 96 330 | Out-Null
$tip3.ForeColor = $GREY

New-RowLabel $gPlan "学习时最多延后" 14 130 104 | Out-Null
$nWait = New-Num $gPlan 124 128 ([int]("0" + $cfg.study_max_wait_min)) 0 300 5
New-RowLabel $gPlan "分钟" 198 130 36 | Out-Null
$tip4 = New-RowLabel $gPlan "0 = 一直等到退出学习软件" 240 130 330 | Out-Null
$tip4.ForeColor = $GREY

$cbSmart = New-Object Windows.Forms.CheckBox
$cbSmart.Text = "识别当前全屏的程序 / 网页（学习、娱乐自动区分）"
$cbSmart.SetBounds(14, 164, 540, 24)
$cbSmart.Checked = [bool]$cfg.smart_scene
$gPlan.Controls.Add($cbSmart)

$cbCam = New-Object Windows.Forms.CheckBox
$cbCam.Text = "用摄像头判断孩子是否真的坐在屏幕前"
$cbCam.SetBounds(14, 190, 540, 24)
if ($cfg.PSObject.Properties.Name -contains "use_camera") { $cbCam.Checked = [bool]$cfg.use_camera } else { $cbCam.Checked = $true }
$gPlan.Controls.Add($cbCam)

# --- 学习软件 ---
$gApps = New-Group "学习软件（到点先不打断，等退出这些程序再休息）" 336 164
$appsTip = New-Object Windows.Forms.Label
$appsTip.Text = "每行一个进程名或名称关键词，例如 anki.exe、学习通、coursera"
$appsTip.ForeColor = $GREY
$appsTip.SetBounds(14, 20, 556, 20)
$gApps.Controls.Add($appsTip)

$tbApps = New-Object Windows.Forms.TextBox
$tbApps.Multiline = $true
$tbApps.ScrollBars = "Vertical"
$tbApps.SetBounds(14, 44, 556, 104)
$tbApps.Font = New-Object Drawing.Font("Consolas", 10)
$tbApps.BackColor = [Drawing.Color]::White
$appsText = ""
if ($cfg.PSObject.Properties.Name -contains "study_apps") {
    foreach ($a in $cfg.study_apps) { $appsText = $appsText + "$a`r`n" }
}
if ($appsText -eq "") {
    $appsText = "anki.exe`r`n学习通`r`nchaoxing.exe`r`ncoursera.exe"
}
$tbApps.Text = $appsText.TrimEnd()
$gApps.Controls.Add($tbApps)

# --- 今日情况 ---
$gToday = New-Group "今日情况" 510 86
$lblToday = New-Object Windows.Forms.Label
$lblToday.Text = "读取中…"
$lblToday.Font = New-Object Drawing.Font("Microsoft YaHei UI", 10.5)
$lblToday.ForeColor = [Drawing.Color]::FromArgb(40, 44, 42)
$lblToday.SetBounds(14, 24, 556, 50)
$gToday.Controls.Add($lblToday)

function Update-Today {
    $st = Read-Json $statePath $null
    if ($null -eq $st) {
        $lblToday.Text = "学习端还没运行过，暂无数据"
        return
    }
    $mins = 0
    if ($st.watched_today) { $mins = [int]([int]$st.watched_today / 60) }
    $breaks = 0
    if ($st.breaks) { $breaks = [int]$st.breaks }
    $sceneName = @{ study = "学习中"; entertainment = "娱乐中"; work = "工作中"; normal = "普通" }[[string]$st.scene]
    if (-not $sceneName) { $sceneName = "普通" }
    $age = 99999
    if ($st.updated) { $age = [int]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - [int]$st.updated) }
    if ($age -gt 120) {
        $live = "学习端没在运行（最近一次 " + $age + " 秒前）"
    } else {
        $live = $sceneName
        if ($st.exe) { $live = $live + "（" + $st.exe + "）" }
        if ($st.pending) { $live = $live + " · 待休息" }
    }
    $lblToday.Text = "专注 " + $mins + " 分钟 · 休息 " + $breaks + " 次`r`n当前：" + $live
}
Update-Today

# --- 外观 ---
$gLook = New-Group "外观" 606 70
$colorValue = "#12644A"
if ($cfg.theme_color) { $colorValue = [string]$cfg.theme_color }
if ($colorValue.Length -ne 7) { $colorValue = "#12644A" }

$swatch = New-Object Windows.Forms.Panel
$swatch.SetBounds(14, 26, 46, 26)
$swatch.BackColor = [Drawing.ColorTranslator]::FromHtml($colorValue)
$swatch.BorderStyle = "FixedSingle"
$gLook.Controls.Add($swatch)

$btnColor = New-Object Windows.Forms.Button
$btnColor.Text = "选择颜色…"
$btnColor.SetBounds(72, 24, 110, 30)
$gLook.Controls.Add($btnColor)

$lblHex = New-Object Windows.Forms.Label
$lblHex.Text = $colorValue
$lblHex.ForeColor = $GREY
$lblHex.SetBounds(194, 30, 200, 22)
$gLook.Controls.Add($lblHex)

$btnColor.Add_Click({
    $dlg = New-Object Windows.Forms.ColorDialog
    $dlg.Color = [Drawing.ColorTranslator]::FromHtml($script:colorValue)
    $dlg.FullOpen = $true
    if ($dlg.ShowDialog() -eq "OK") {
        $script:colorValue = "#" + $dlg.Color.R.ToString("X2") + $dlg.Color.G.ToString("X2") + $dlg.Color.B.ToString("X2")
        $swatch.BackColor = $dlg.Color
        $lblHex.Text = $script:colorValue
    }
})

# --- 底部按钮 ---
$lblStatus = New-Object Windows.Forms.Label
$lblStatus.Text = ""
$lblStatus.ForeColor = $GREEN
$lblStatus.SetBounds(20, 692, 360, 22)
$form.Controls.Add($lblStatus)

$btnPin = New-Object Windows.Forms.Button
$btnPin.Text = "修改家长密码"
$btnPin.SetBounds(18, 716, 124, 34)
$form.Controls.Add($btnPin)

$btnSave = New-Object Windows.Forms.Button
$btnSave.Text = "保存"
$btnSave.SetBounds(408, 716, 92, 34)
$btnSave.BackColor = $GREEN
$btnSave.ForeColor = [Drawing.Color]::White
$btnSave.FlatStyle = "Flat"
$form.Controls.Add($btnSave)

$btnClose = New-Object Windows.Forms.Button
$btnClose.Text = "关闭"
$btnClose.SetBounds(510, 716, 92, 34)
$form.Controls.Add($btnClose)

$btnClose.Add_Click({ $form.Close() })

$btnSave.Add_Click({
    $apps = @()
    foreach ($line in ($tbApps.Text -split "[`r`n,;，、]+")) {
        $t = $line.Trim().ToLower()
        if ($t -ne "" -and $apps -notcontains $t) { $apps += $t }
    }
    if ($apps.Count -eq 0) { $apps = @("anki.exe") }

    Set-Field $script:cfg "interval_min" ([int]$nInterval.Value)
    Set-Field $script:cfg "break_sec" ([int]$nBreak.Value)
    Set-Field $script:cfg "entertainment_min" ([int]$nEnt.Value)
    Set-Field $script:cfg "study_max_wait_min" ([int]$nWait.Value)
    Set-Field $script:cfg "smart_scene" ([bool]$cbSmart.Checked)
    Set-Field $script:cfg "use_camera" ([bool]$cbCam.Checked)
    Set-Field $script:cfg "theme_color" $script:colorValue
    Set-Field $script:cfg "study_apps" @($apps)

    Write-JsonUtf8 $cfgPath $script:cfg
    Update-Today
    $lblStatus.Text = "已保存 · 学习端约 1 秒后生效"
})

$btnPin.Add_Click({
    $cur = $script:cfg.admin_pin_sha256
    if ($cur -and "$cur".Length -gt 0) {
        $a = New-PinDialog "当前密码" $false
        if (-not $a[2]) { return }
        if ((Get-PinHash $script:cfg.admin_salt $a[0]) -ne $cur) { Show-Msg "密码不对"; return }
    }
    $b = New-PinDialog "新密码（留空 = 取消密码）" $false
    if (-not $b[2]) { return }
    if ($b[0] -eq "") {
        if ([Windows.Forms.MessageBox]::Show("取消密码后孩子可以直接改设置、也能退出。确定吗？", $TITLE, "YesNo", "Warning") -ne "Yes") { return }
        Set-Field $script:cfg "admin_salt" ""
        Set-Field $script:cfg "admin_pin_sha256" ""
        Write-JsonUtf8 $cfgPath $script:cfg
        $lblStatus.Text = "已取消密码 · 学习端限制不再生效"
        return
    }
    if ($b[0].Length -lt 4) { Show-Msg "密码至少 4 位"; return }
    $c = New-PinDialog "再输入一次" $false
    if (-not $c[2]) { return }
    if ($b[0] -ne $c[0]) { Show-Msg "两次输入不一致"; return }
    $salt = -join ((48..57) + (97..102) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
    Set-Field $script:cfg "admin_salt" $salt
    Set-Field $script:cfg "admin_pin_sha256" (Get-PinHash $salt $b[0])
    Write-JsonUtf8 $cfgPath $script:cfg
    $lblStatus.Text = "密码已更新"
})

$timer = New-Object Windows.Forms.Timer
$timer.Interval = 5000
$timer.Add_Tick({ Update-Today })
$timer.Start()

$form.Add_FormClosed({ $timer.Stop() })
[void]$form.ShowDialog()
