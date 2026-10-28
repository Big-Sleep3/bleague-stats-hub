/* University Recruiting Hub / UI language layer. English UI only; official player names stay as published. */
(()=>{'use strict';
const KEY='urh-ui-language', raw={
'公開の成績と、スタッフ限定の評価データを分離':'Public statistics are separated from staff-only evaluations.',
'管理者による初期設定が必要':'Administrator setup required',
'スタッフログイン':'Staff sign in',
'メールのワンタイムリンクで認証する。登録後、管理者に承認されたスタッフだけが閲覧・編集可能。':'Sign in using a one-time email link. Only approved staff can view and edit.',
'メールアドレス':'Email address','ログインリンクを送る':'Send sign-in link',
'管理者の承認待ち':'Awaiting administrator approval',
'アカウントは認証されたけど、スタッフ共有データへのアクセスは未承認だよ。':'Signed in, but this account has not been approved for staff access.',
'ログアウト':'Sign out','選手を選んでね。':'Choose a player.',
'名前・大学名で検索':'Search player or university','学年':'Year','未確認':'Unverified',
'1年':'Year 1','2年':'Year 2','3年':'Year 3','4年':'Year 4',
'身長 cm':'Height (cm)','優先度':'Priority','優先順位':'Priority','未設定':'Not set',
'ステージ':'Stage','未評価':'Not evaluated','映像収集':'Film collection','一次評価':'Initial evaluation',
'追加視察':'Further scouting','面談候補':'Interview candidate','保留':'On hold','対象外':'Not a candidate',
'非公開スカウトメモ':'Private scouting notes','映像リンク':'Film links','映像追加':'Add film',
'削除':'Remove','最新を取得':'Reload latest','共有評価を保存':'Save shared evaluation',
'保存先：このブラウザのみ':'Stored on this browser only',
'全候補を見る':'View all players','全候補を表示':'View all players',
'選手を継続追跡するための4ステップ':'Four steps for continuous player tracking',
'実名・学年・卒業年度・ポジションを一次ソースで照合。未確認は未確認のまま。':'Verify names, class years, graduation years and positions against primary sources. Leave unknowns unknown.',
'フルゲーム優先で視聴。PnR、Shoot、Defense、Decision等を記録。':'Prioritize full games; tag PnR, shooting, defense and decisions.',
'定量指標とプロへの適応を分けて評価し、3選手まで比較。':'Separate statistical production from pro projection; compare up to three players.',
'3年生以下も同じIDで追跡。新しいシーズンの成績と視察履歴を追加。':'Keep stable player IDs through graduation; add season-by-season results and notes.',
'名前を選ぶと選手ページを表示。比較は最大3名まで。':'Select a name to open the profile. Compare up to three players.',
'選手名・大学・IDで検索':'Search player, university or ID','選手検索':'Player search',
'すべての学年':'All class years','学年未確認':'Year unverified','すべての大学':'All universities',
'全ポジション':'All positions','選手名順':'Name A–Z','比較':'Compare','選手 / 大学':'Player / university',
'学年区分':'Class group','優先':'Priority','評価':'Rating','条件に一致する選手はいないよ。':'No players match these filters.',
'要確認':'Verify','即戦力候補':'Immediate prospects','中長期追跡':'Long-term tracking',
'登録候補者':'Players tracked','学年を要確認':'Class year to verify','公開リンク＋手動追加':'Public links + manually added',
'候補を選ぶ':'Select players','比較したい選手はPLAYER BOARDのチェックボックスから選択（最大3名）。':'Use the checkboxes on PLAYER BOARD (up to three players).',
'映像は外部リンク。無断複製・再配布はしない。':'External video links only. Do not copy or redistribute without permission.',
'相手未確認':'Opponent unverified','Timecode未登録':'No timecode','追加リンク':'Added link',
'映像を見る ↗':'Watch film ↗','選手詳細':'Player profile','映像リンクはまだ登録されていないよ。':'No film links have been added yet.',
'映像登録なし':'No films recorded','卒業年度':'Graduation year',
'端末内に保存':'Saved locally','次のチェック日':'Next review date',
'強み、プロでも再現できそうな武器':'Strengths that may translate to pro basketball',
'確認したい課題・弱点':'Questions, weaknesses and risk factors',
'次回視察・確認項目':'Next evaluation or film review','未採点':'Not rated',
'未採点（9項目が必要）':'Unrated (nine ratings required)',
'評価・候補情報を保存':'Save local scouting profile','保存先：このブラウザのみ':'Saved on this browser only',
'試合日':'Game date','対戦相手':'Opponent','タイムコード':'Timecode',
'映像メモ':'Film notes','映像リンクを追加':'Add film link','大会':'Competition',
'ソース':'Source','開く':'Open','公式データの出典 ↗':'Official source ↗',
'2026 学年':'2026 class year','学年を確認':'Verify class year',
'条件に一致する選手はいないよ。':'No matching players.',
'公式スタッツの取得時点を保存。原則として大会・年度を混ぜてランキングしない。':'Keep source timestamps and do not mix competitions or seasons in rankings.',
'学年、身長、ポジション、スカウト評点は欠測なら空欄。未確認を勝手に補完しない。':'Keep unverified class years, heights, positions and grades blank. Never guess missing information.',
'記入した評価・優先順位・メモはこの端末のブラウザ内だけ。ほかの端末・スタッフには同期されない。':'Public-board evaluations are stored only in this browser and do not sync with staff accounts.',
'評価データはJSON書き出しでバックアップ。読み込むと現在のローカル記録を置き換える。':'Export JSON to back up local notes. Import replaces this browser’s existing notes.',
'この公開型プロトタイプは認証・権限管理・暗号化・チーム共有を備えていない。機密性の高いスカウティング情報は、正式な安全な保存先が整うまで入力しないでね。':'This public board has no team access controls. Use the protected staff portal for confidential evaluations.',
'公式データの出典':'Official data source','初期サンプル：':'Initial sample:','指標':'Metrics','今後の拡張':'Planned additions',
'学年の一次ソース照合、関西ほかの大学リーグ対応、試合ごとのBOXスコア、公式更新の検知、スタッフアカウントと権限付きクラウド共有。':'Verify class years, expand league coverage, add game box scores and enhance film tracking.',
'関東大学バスケットボール連盟・2026個人成績':'Kanto University League 2026 official player statistics',
'未保存の変更を破棄して移動する？':'Discard unsaved changes and switch players?',
'未保存の変更を破棄する？':'Discard unsaved changes?',
'メールのログインリンクを確認してね':'Check your inbox for the sign-in link.',
'ログインリンクを確認してね':'Check your email for the sign-in link.',
'共有保存完了':'Shared data saved','最新情報を取得したよ':'Latest data loaded.',
'映像登録なし':'No films added','すべての映像':'All films','タグ・選手・大学で検索':'Search films by tag, player or university',
'共有の映像リンク':'Shared film links','登録映像':'Film library',
'映像の種類':'Film type','映像タグ':'Film tag','映像メモ・見どころ':'Film note / what to watch',
'動画URL':'Video URL','日付':'Date','削除する':'Remove',
'関東大学1部':'Kanto Division 1','関東大学2部':'Kanto Division 2','関西学生1部':'Kansai Division 1','関西学生2部':'Kansai Division 2',
'取り込み済み':'Imported','公式リンクのみ':'Source linked only','自動更新対象':'Auto-updated','確認待ち':'Pending verification',
'公式スタッツを見る':'View official statistics','大会情報を見る':'View competition info','公式配信を見る':'View official videos',
'他リーグの入口':'Other league sources','公式ソース一覧':'Official league sources','選手データ':'Player data',
'ソース一覧':'Source directory','一覧へ戻る':'Back to player board'
};
const exact=new Map(Object.entries(raw));
for(const [k,v] of Object.entries({"＋ 他リーグの候補を手動登録（スタッフ限定）":"+ Add candidates from other leagues (staff only)","関東2部・関西・地方大学など。未確認の成績をゼロ点として登録しない。":"For Kanto Division 2, Kansai and regional universities. Missing statistics are never counted as zero.","選手名":"Player name","大学名":"University","リーグ・大会":"League / competition","候補選手を登録":"Add prospect","登録完了":"Prospect added","登録失敗:":"Unable to add: ","FILM LIBRARY — 共有映像を検索":"FILM LIBRARY — Search shared links","承認されたスタッフ間で登録映像を共有。動画自体は保存せずリンクのみ管理。":"Share links and scouting notes with approved staff. Video files are not stored here.","該当する映像はまだないよ。":"No matching films yet.","大学生の即戦力候補と将来候補を、同じIDで継続追跡。公式スタッツ、公開映像リンク、年度別成長と評価記録をまとめる。":"Track senior and younger college prospects using stable player IDs, official stats, video links and year-to-year assessments.","初期収録：関東大学1部 得点上位30名":"Initial coverage: Kanto Division 1 — top 30 scorers","非公式の分析用プロトタイプ。公式団体・リーグの運営サイトではありません。数値は競技会と収録時点に依存します。":"Unofficial scouting tool. Not operated by a league or university federation. Figures depend on competition and reporting date.","評価データを書き出す":"Export local evaluations","バックアップを読み込む":"Import local backup","STAFF LOGIN / 非公開スカウト評価":"STAFF LOGIN / Private scouting","公式リーグ・スタッツ・映像の入口":"Official leagues, statistics and film sources","リンク先は各連盟が管理する公式ページ。候補選手の成績を確認してから登録するための入口だよ。":"Official federation resources for verifying prospects before adding them.","2026年度 / 個人成績。関東1部の公開ランキングから選手を取り込み、自動更新する設定。":"2026 statistics. Kanto Division 1 published player results are imported through scheduled checks.","掲載範囲：":"Coverage:","公式スタッツ表に掲載された選手。登録全員ではない。":"Players shown in the official statistics table — not the full registered roster.","2026年度 / 公式大会ページを収録。個人データの一括取り込みは未実装。":"2026 official competition page is linked. Bulk player import is not implemented.","公式BOX・スタッツの掲載内容を確認し、選手をSTAFFから手動登録できる。":"Review the official box score or statistics, then manually add a prospect in STAFF.","2026年度 / 公式の試合結果、スタッツランキング、映像配信案内あり。個人成績はまだ未取り込み。":"2026 results, rankings and video information are available from the federation. Player stats have not been imported.","公式動画へのリンクを個別選手の映像記録に紐づけられる。":"Link official video footage to individual player film logs.","2026年度 / 公式大会ページと配信情報を確認できる。個人スタッツの一括取り込みは未実装。":"2026 official competition and streaming information linked. Bulk import is not implemented.","映像の見逃し配信は連盟の案内から確認できる。":"Check the federation page for replay footage.","収録範囲を混同しないでね。":"Do not mix coverage:","現在の公開選手ランキングは関東1部だけ。2部・関西の公式リンクを追加しても、当該リーグの数値が比較テーブルに自動で加わるわけではない。手動登録した候補はSTAFFのみ表示し、成績未確認の選手はゼロ点扱いしない。":"The public player rankings currently cover Kanto Division 1 only. Source links do not import additional stats. Manually added prospects are staff-only; missing results are not treated as zero.","同じ選手を同時編集した場合は最後の保存が優先されるよ。":"If multiple staff edit the same player, the latest save wins.","強み・課題・チームへの適合度など":"Strengths, weaknesses and team fit","身長 cm":"Height (cm)"}))exact.set(k,v);

for(const [k,v] of Object.entries({"関東2部：公式データ検証待ち。まだ候補人数に加えていないよ。":"Kanto Division 2: awaiting verified official data; players are not yet counted.","関東2部：公式データ検証待ち。未確認の数値は表示しないよ。":"Kanto Division 2: awaiting official verification; no unverified figures are shown.","公式ソース一覧 ↗":"Official sources ↗","公式大会スタッツから集計 · 3P% は3PM÷3PA · 異なるリーグの水準に注意":"Calculated from official league stats · 3P% = 3PM / 3PA · Consider division strength.","選手・大学名で検索":"Search player or university","すべてのリーグ":"All leagues","各指標は所属リーグの2026年度累計。3PA 0本の場合の3P%は —。未掲載のPF/OREB等も — で表示。":"Metrics use 2026 season totals within each league. 3P% is — with no attempts; missing PF/OREB data are —.","公式データ検証待ち":"Awaiting verified stats","2026年度 / 公式個人成績の検証付き自動取得を設定。成功したデータだけ公開ページに収録。":"The 2026 official player-stat importer has validation gates. Only verified results appear on the public board.","取り込み済み":"Imported","同じリーグ内で比較":"Compare within a league","2026 公式リーグ戦 · 異なるDiv.の比較は競技レベルに注意":"2026 official league play · account for competition level when comparing divisions","公式スタッツの出典":"Official statistics source","関東大学2部：公式検証済み":"Kanto Division 2: verified","リーグ戦の成績":"League statistics","初期30名のPPG順":"Initial 30 players, by points per game","大会別に比較":"Compare by competition","並び替え":"Sort by","学年は未確認":"Class year unverified","公式記録を確認":"Verify official records","新しい公式データ":"New official data","選手データの収録状況":"Player coverage status","得点":"Points","総得点":"Total points","リバウンド":"Rebounds","アシスト":"Assists","スティール":"Steals","ブロック":"Blocks","ターンオーバー":"Turnovers","割合":"Percentage","公式大会データ":"Official competition data","公開映像リンク":"Public video links","選手情報":"Player information","公式スタッツから取得":"From official statistics"}))exact.set(k,v);
exact.set('公式スタッツをCSVに書き出したよ','Exported official stats as a CSV file.');
const patterns=[
[/^(\d+)\s*人$/,'$1 players'],
[/^NOW\s*\/\s*(\d)年$/,'NOW / Year $1'],
[/^FUTURE\s*\/\s*(\d)年$/,'FUTURE / Year $1'],
[/^(\d+)名の4年生のみ。/,'only $1 confirmed seniors. '],
[/^映像の数：\s*(\d+)$/,'Film count: $1'],
[/^学年が確認できているのは現在(\d+)名の4年生のみ。ほかの(\d+)名は未確認で、下級生としてカウントしていないよ。$/,'Currently only $1 seniors are verified. The other $2 players have unverified class years and are not counted as underclassmen.'],
[/^([A-Z0-9.%/]+) 順$/,'Sort: $1'],
[/^関東大学2部：公式検証済み (\d+)名を追加 · 2026リーグ戦の成績$/,'Kanto Division 2: $1 verified players imported (2026 league season)'],
[/^取り込み済み (\d+)名$/,'Imported $1 players'],
[/^公式スタッツ /,'Official stats '],
[/^読み込み失敗:/,'Load failed:'],
[/^保存失敗:/,'Save failed:'],
[/^送信失敗:/,'Send failed:'],
[/^対戦相手:/,'Opponent:']
];
function translate(s){if(!s||!s.trim())return s; const leading=s.match(/^\s*/)[0],trailing=s.match(/\s*$/)[0],core=s.trim();if(exact.has(core))return leading+exact.get(core)+trailing;for(const [re,fmt] of patterns){if(re.test(core))return leading+core.replace(re,fmt)+trailing}return s}
let lang='ja';try{lang=localStorage.getItem(KEY)==='en'?'en':'ja'}catch{}
const memo=new WeakMap(),attrs=new WeakMap();
function handleText(node){if(!node.nodeValue||!node.nodeValue.trim()||node.parentElement?.closest('script,style,textarea,[data-no-translate]'))return;
let m=memo.get(node);if(!m||node.nodeValue!==m.rendered){m={source:node.nodeValue,rendered:node.nodeValue};memo.set(node,m)}
const value=lang==='en'?translate(m.source):m.source;
if(node.nodeValue!==value)node.nodeValue=value;m.rendered=value
}
function handleAttr(el,attr){const value=el.getAttribute(attr);if(!value)return;let m=attrs.get(el);if(!m){m={};attrs.set(el,m)}if(!m[attr]||m[attr].rendered!==value)m[attr]={source:value,rendered:value};const next=lang==='en'?translate(m[attr].source):m[attr].source;
if(next!==value)el.setAttribute(attr,next);m[attr].rendered=next
}
function sweep(root=document.body){if(!root)return;const list=[];if(root.nodeType===1)list.push(root);
if(root.querySelectorAll)list.push(...root.querySelectorAll('*'));
for(const el of list){if(el.matches('script,style,textarea,[data-no-translate]')||el.closest('script,style,textarea,[data-no-translate]'))continue;
if(el.tagName==='OPTION'&&!el.hasAttribute('value'))el.setAttribute('value',el.textContent.trim());
for(const a of ['placeholder','aria-label','title'])if(el.hasAttribute(a))handleAttr(el,a);
for(const c of el.childNodes)if(c.nodeType===Node.TEXT_NODE)handleText(c)}
}
function controls(){if(document.getElementById('urh-language-control'))return;const head=document.querySelector('.mast-inner')||document.querySelector('header')||document.body;
const c=document.createElement('div');c.id='urh-language-control';c.setAttribute('aria-label','Language / 言語');c.setAttribute('data-no-translate','');
c.style.cssText='display:inline-flex;gap:4px;align-items:center;margin-left:auto;border:1px solid #9bb9bb;border-radius:9px;padding:3px;background:#ffffff13;flex-shrink:0;';
for(const mode of ['ja','en']){const b=document.createElement('button');b.type='button';b.textContent=mode==='ja'?'日本語':'English';b.dataset.lang=mode;b.style.cssText='font:700 12px sans-serif;border:0;border-radius:7px;padding:8px 12px;cursor:pointer;background:transparent;color:#fff;';b.onclick=()=>setLanguage(mode);c.appendChild(b)}
if(head.tagName==='HEADER'){head.style.display='flex';head.style.alignItems='center';head.style.gap='14px';head.appendChild(c)}else head.appendChild(c);
buttons();
}
function buttons(){document.querySelectorAll('#urh-language-control button').forEach(b=>{const active=b.dataset.lang===lang;b.style.background=active?'#fff':'transparent';b.style.color=active?'#153447':'#fff';b.setAttribute('aria-pressed',String(active))})}
function setLanguage(next){lang=next;document.documentElement.lang=lang;try{localStorage.setItem(KEY,lang)}catch{};buttons();sweep()}
const obs=new MutationObserver(muts=>{let need=false;for(const m of muts){if(m.target.closest?.('#urh-language-control'))continue;if(m.type==='childList'||m.type==='characterData'){need=true;break}}if(need){if(!document.getElementById('urh-language-control'))controls();sweep()}});
function init(){controls();setLanguage(lang);obs.observe(document.body,{childList:true,subtree:true,characterData:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
window.URHLanguage={setLanguage,getLanguage:()=>lang,translate};
})();