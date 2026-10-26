// Optional local authoring with the Codex bundled @oai/artifact-tool runtime.
// RUNTIME_NODE_MODULES selects the bundled node_modules; no production dependency.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const runtime = process.env.RUNTIME_NODE_MODULES;
const require = createRequire(runtime ? path.join(runtime, '__runtime__.cjs') : import.meta.url);
const {Presentation, PresentationFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const data = JSON.parse(await fs.readFile(path.join(root, 'results/benchmark.json'), 'utf8'));
const records = new Map(data.results.map(r => [`${r.level}/${r.algorithm}`, r]));
const build = path.join(root, 'tmp/slides');
await fs.mkdir(build, {recursive: true});
const deck = Presentation.create({slideSize: {width: 1280, height: 720}});
const ink = '#203d35', green = '#244e42', muted = '#61745d', paper = '#f7f8f2';
const notes = [];

function text(slide, value, x, y, width, height, size=28, bold=false, color=ink) {
  const shape = slide.shapes.add({geometry: 'textbox', position: {left:x, top:y, width, height},
    fill: 'none', line: {fill:'none', width:0}});
  shape.text = value;
  shape.text.style = {typeface:'Arial', fontSize:size, bold, color, insets:0,
    verticalAlignment:'top', autoFit:'none', wrap:'square'};
  return shape;
}
function slide(title, note, source='docs/REPORT.md; results/benchmark.json') {
  const s = deck.slides.add();
  s.background.fill = paper;
  text(s, title, 64, 45, 1152, 100, 46, true);
  text(s, `MẠCH / BTL1                                       ${String(deck.slides.items.length).padStart(2,'0')}`, 64, 673, 1152, 26, 16, false, muted);
  s.speakerNotes.text = `${note}\n\nNguồn: ${source}`;
  notes.push({title, note, source});
  return s;
}
async function screenshot(s, name, position) {
  const bytes = await fs.readFile(path.join(root,'docs/images',name));
  s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),
    contentType:'image/png', alt:`Ảnh giao diện Mạch: ${name}`, fit:'contain', position});
}
function paragraphs(s, values, x=64, y=170, width=1100, gap=110, size=28) {
  values.forEach((value,i) => text(s,value,x,y+i*gap,width,gap-18,size));
}
function resultsTable(s, ids, y=160) {
  const rows = [['Input','DFS ms','Greedy ms','DFS KiB','Greedy KiB','DFS N','Greedy N']];
  for (const id of ids) {
    const d=records.get(`${id}/dfs`), g=records.get(`${id}/greedy`);
    rows.push([id,d.median_ms.toFixed(3),g.median_ms.toFixed(3),d.peak_python_kib.toFixed(2),g.peak_python_kib.toFixed(2),String(d.expanded),String(g.expanded)]);
  }
  const table = s.tables.add({rows:rows.length, columns:7, left:64, top:y,
    width:1152, height:rows.length*48, columnWidths:[300,140,150,145,155,126,136], values:rows});
  for(let r=0;r<rows.length;r++) for(let c=0;c<7;c++) {
    const cell=table.getCell(r,c);
    cell.fill=r===0?'#e0ead4':r%2?'#ffffff':'#eef2e7';
    cell.text.style={typeface:'Arial',fontSize:20,bold:r===0,color:ink,
      insets:{top:8,bottom:7,left:8,right:8},verticalAlignment:'middle'};
  }
  text(s,'ms: median search · KiB: peak cấp phát Python · N: trạng thái đã xét (gồm đích)',64,620,1152,35,18,false,muted);
}

{
  const s = slide('Mạch - Logic Lab',
    'Giới thiệu hai bài toán và hai chính sách tìm kiếm. Python 3 xử lý toàn bộ search và luật; giao diện chỉ hỗ trợ tương tác. Không tuyên bố tối ưu số nước đi.');
  text(s,'Pipes & Light Up',64,205,1152,100,76,true);
  text(s,'DFS & Greedy Best-First Search',64,330,1152,75,42,false,green);
  text(s,'Bài tập lớn 1 · Nhập môn Trí tuệ nhân tạo\nHọc kỳ 1 năm học 2026-2027',64,490,1152,110,28,false,muted);
}
{
  const s = slide('Pipes: một mạng, không vòng kín',
    'Mỗi ô là một đỉnh của đồ thị. Chỉ tạo cạnh khi hai đầu nối khớp. Nghiệm là cây bao trùm các ô, đồng thời không có đầu hở hoặc nối ra ngoài biên. Ứng dụng chọn bản không nối xuyên biên.',
    'https://www.puzzle-pipes.com/ (25/10/2026); logic_lab/games/pipes.py; docs/images/pipes.png');
  paragraphs(s,['Xoay từng mảnh để mọi đầu ống khớp với ô kề cạnh.',
    'Toàn bộ ống liên thông; không chĩa ra biên và không có chu trình.',
    'Đồ thị nghiệm là cây: n đỉnh, n − 1 cạnh.'],64,175,500,145,29);
  await screenshot(s,'pipes.png',{left:605,top:148,width:600,height:485});
}
{
  const s = slide('Light Up: phủ sáng và thỏa ô số',
    'Đèn chỉ đặt trên ô trắng. Ô đen chặn tia sáng, ô số yêu cầu số đèn kề cạnh chính xác. Hai tia sáng có thể giao nhau nhưng hai đèn không được nhìn nhau. Dấu X không chặn ánh sáng.',
    'https://www.puzzle-light-up.com/ (25/10/2026); logic_lab/games/lightup.py; docs/images/lightup.png');
  paragraphs(s,['Mọi ô trắng đều được chiếu sáng theo hàng hoặc cột.',
    'Hai đèn không chiếu vào nhau; ô đen chặn tia sáng.',
    'Ô số k cần đúng k đèn kề cạnh, không tính đường chéo.'],64,175,500,145,29);
  await screenshot(s,'lightup.png',{left:605,top:148,width:600,height:485});
}
{
  const s = slide('DFS và Greedy dùng chung mô hình',
    'Phân biệt chính sách lấy node khỏi frontier. Hai bên có cùng trạng thái đầu, thứ tự chọn biến, thứ tự giá trị và cắt nhánh. DFS không sắp xếp theo heuristic. Có ngân sách nên limit là chưa biết; chỉ duyệt hết frontier mới chứng minh unsat.');
  const values=[['Đặc điểm','DFS','Greedy'],['Frontier','Stack (LIFO)','Min-heap theo h'],
    ['Chọn biến / sinh con','Cố định hàng/cột','Cùng thứ tự với DFS'],['Cắt nhánh','Ràng buộc khả thi','Cùng quy tắc với DFS'],
    ['Bảo đảm tối ưu','Không','Không; không phải A*']];
  const t=s.tables.add({rows:5,columns:3,left:64,top:175,width:1152,height:310,columnWidths:[360,396,396],values});
  for(let r=0;r<5;r++)for(let c=0;c<3;c++){const cell=t.getCell(r,c);cell.fill=r===0?'#e0ead4':'#ffffff';cell.text.style={typeface:'Arial',fontSize:26,bold:r===0,color:ink,insets:12};}
  text(s,'Không giới hạn tài nguyên: đầy đủ trên miền hữu hạn.\nCó giới hạn: limit ≠ vô nghiệm.',64,525,1152,95,29,true);
}
{
  const s = slide('Pipes: gán hướng cuối cùng',
    'Tuple gồm hướng đã gán hoặc 0 cho chưa gán. Các hướng đối xứng được loại trùng. Một bước search gán một ô, có thể tương đương nhiều lần xoay trên UI. Điểm h xếp hạng theo số biến chưa gán và kích thước miền; không là cận tối ưu thao tác.');
  paragraphs(s,['Bitmask: trên 1 · phải 2 · dưới 4 · trái 8\n0 trong search: chưa gán hướng.',
    'Cắt nhánh: đầu hở, miền rỗng, chu trình đã có,\nđồ thị các cạnh còn khả thi không liên thông.'],64,170,1152,135,30);
  text(s,'h(s) = Σ [1 + 0.25 × (|Dᵢ| − 1)]',64,470,1152,75,42,true,green);
  text(s,'Tổng trên các ô chưa gán; Dᵢ là miền hướng còn lại.',64,560,1152,50,26,false,muted);
}
{
  const s = slide('Light Up: quyết định có đặt đèn',
    'Chỉ ô trắng là biến -1/0/1. Tiền xử lý tập nhìn thấy. Thử không đèn trước, có đèn sau nếu còn hợp lệ. Đích có thể đạt khi còn biến -1, hiểu là không đặt thêm đèn. Một bóng đèn thỏa nhiều mục tiêu nên h có thể đếm chồng.');
  paragraphs(s,['−1: chưa quyết định · 0: không có đèn · 1: có đèn\nTính trước tập ô nhìn thấy và hàng xóm của ô số.',
    'Cắt nhánh: đèn nhìn nhau, vượt/thiếu khả năng đạt ô số,\nô chưa sáng không còn ứng viên chiếu tới.'],64,170,1152,135,29);
  text(s,'h(s) = ô chưa sáng + tổng đèn còn thiếu',64,470,1152,75,38,true,green);
  text(s,'Hàm xếp hạng; không bảo đảm ít đèn hay ít nước đi nhất.',64,560,1152,55,26,false,muted);
}
{
  const s = slide('Demo là lịch sử xét trạng thái',
    'Demo phát tối đa 350 trạng thái lấy ra khỏi frontier. Đây không phải đường nghiệm: trạng thái liền nhau có thể là nhánh khác nhau. Nghiệm cuối nằm ở nút riêng. Bảng người chơi không đổi khi xem demo; ống mờ là hướng minh họa chưa được gán.',
    'web/app.js; logic_lab/search.py; docs/images/demo.png');
  await screenshot(s,'demo.png',{left:64,top:150,width:785,height:480});
  paragraphs(s,['Lùi/tiến, tự chạy,\nthanh trượt.',
    'Có thể chuyển nhánh\ngiữa hai bước.',
    'Xem nghiệm riêng;\nbảng chơi giữ nguyên.'],900,185,310,145,28);
}
{
  const s = slide('Thực nghiệm có dữ liệu tái lập',
    '26 input gồm 8 màn chơi và 18 input: hai game x kích thước 4,6,8 x seed 101,102,103. Mỗi tổ hợp warm-up rồi 7 mẫu thời gian, lấy median; memory chạy riêng sau gc.collect. Cả 364 lượt time và 52 lượt memory solved và được check. Đo search không gồm khởi tạo/HTTP/UI/trace. Các khác biệt rất nhỏ có thể là nhiễu.');
  paragraphs(s,['26 input × 2 thuật toán × 7 lần = 364 lượt thời gian\nThêm 52 lượt đo bộ nhớ riêng; tất cả có nghiệm hợp lệ.',
    'Python 3.12.14 · Windows 11\nWarm-up, median 7 mẫu; lưu input, mẫu thô và mã băm.',
    '4 giây / 100000 trạng thái; lần đo bộ nhớ 30 giây\nPeak cấp phát Python trong search, không phải RSS.'],64,170,1152,145,30);
}
{
  const s = slide('Pipes: cắt nhánh chi phối kết quả',
    'Bảng hiển thị bốn màn tương tác và một input 8x8, không thay cho bảng toàn bộ trong phụ lục báo cáo. Trên 13 input Pipes, DFS xét 453 trạng thái, Greedy 455. Nhiều miền chỉ còn một giá trị nên heuristic ít đổi thứ tự. Tổng median từng input DFS 49.331 ms, Greedy 53.001 ms. Không suy rộng từ chênh lệch nhỏ.');
  resultsTable(s,['pipes-3','pipes-4','pipes-5','pipes-6','pipes-8-seed-103']);
  text(s,'13 input: DFS xét 453 trạng thái; Greedy xét 455.\nNhiều hướng bị ràng buộc sớm, heap và h ít tạo lợi thế.',64,500,1152,95,29);
}
{
  const s = slide('Light Up: lợi ích tùy cấu trúc input',
    'Bảng trích toàn bộ bốn màn tương tác và ba input 8x8. Bảng 13 input đầy đủ nằm trong phụ lục. Seed 102 là trường hợp Greedy có lợi rõ; lightup-7 là phản ví dụ. Peak cấp phát bao gồm cấu trúc được tạo trong search và không đồng nhất frontier_peak.');
  resultsTable(s,['lightup-3','lightup-5','lightup-6','lightup-7','lightup-8-seed-101','lightup-8-seed-102','lightup-8-seed-103']);
  text(s,'Greedy giảm nhiều nhánh ở 8×8 seed 102; tăng nhánh ở lightup-7.',64,570,1152,42,25,true);
}
{
  const s = slide('Heuristic có thể giúp hoặc gây lệch hướng',
    'Biểu đồ số trạng thái xét, hai thang trục độc lập: không so độ cao cột giữa hai biểu đồ. Lightup-7: DFS 51, Greedy142; seed102: DFS1584, Greedy68. Heuristic không biết toàn bộ tương tác ràng buộc tương lai nên giảm h cục bộ không đảm bảo ít node hơn.');
  for(const [i,id] of ['lightup-7','lightup-8-seed-102'].entries()){
    text(s,id,64+i*590,155,550,45,27,true);
    const chart=s.charts.add('bar',{position:{left:64+i*590,top:220,width:550,height:330},
      categories:['DFS','Greedy'],series:[{name:'Trạng thái đã xét',values:['dfs','greedy'].map(a=>records.get(`${id}/${a}`).expanded),fill:green}],
      hasLegend:false,barOptions:{direction:'column',grouping:'clustered'},
      chartFill:paper,plotAreaFill:paper,
      xAxis:{textStyle:{typeface:'Arial',fontSize:23}},
      yAxis:{minimumScale:0,textStyle:{typeface:'Arial',fontSize:18}},
      dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:'Arial',fontSize:24}}});
    for(const style of [chart.xAxis.textStyle,chart.yAxis.textStyle,chart.dataLabels.textStyle]) style.typeface='Arial';
  }
  text(s,'Hai biểu đồ dùng thang trục độc lập. Nguồn: benchmark, cùng chính sách cắt nhánh.',64,590,1152,48,20,false,muted);
}
{
  const s = slide('Kiểm chứng và demo trực tiếp',
    'Chạy python app.py. Demo 1: Pipes chọn DFS, xem vài trạng thái và nghiệm cuối. Demo 2: LightUp3 đặt đèn cạnh số0, xin gợi ý sửa, áp dụng rồi giải tiếp. Kết thúc bằng so sánh hai case heuristic. 47 unit tests và 800 so luật, Chromium thực tế; không khẳng định không còn lỗi. Chưa kiểm Safari/Firefox hay cảm ứng vật lý. Thông tin nhóm cần bổ sung trước nộp.',
    'tests/; docs/QA_RESULTS.md; https://www.puzzle-pipes.com/; https://www.puzzle-light-up.com/');
  paragraphs(s,['47 test Python · 800 đối chiếu luật Python/JavaScript\nChromium: 16 demo, bàn phím, gợi ý, lưu tiến độ, 4 cỡ màn.',
    'Demo: Pipes → DFS / Greedy → bước xét / lời giải\nLight Up 3×3 → đặt đèn cạnh số 0 → gợi ý sửa → giải tiếp.',
    'Giới hạn: bộ sinh có nghiệm, không chứng minh duy nhất;\nkhông tối ưu thao tác; chưa kiểm Safari/Firefox/cảm ứng.'],64,170,1152,145,29);
}

for(const [i,s] of deck.slides.items.entries()){
  const png=await deck.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
await (await PresentationFile.exportPptx(deck)).save(path.join(build,'candidate.pptx'));
await fs.writeFile(path.join(root,'docs/PRESENTATION.md'), '# Nội dung thuyết trình\n\n'+notes.map((n,i)=>`## ${i+1}. ${n.title}\n\n${n.note}\n\nNguồn: ${n.source}\n`).join('\n'));
try {
  await fs.writeFile(path.join(build,'slides.pdf'),new Uint8Array(await (await deck.export({format:'pdf'})).arrayBuffer()));
} catch (error) {
  console.warn(`Native PDF export unavailable: ${error.message}. Run python tools/build_slide_pdf.py for a rendered PDF.`);
}
console.log(`Saved ${deck.slides.items.length} slides to ${build}`);
