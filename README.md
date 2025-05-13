# CONTRASHOOTER
---

## TỔNG QUAN

### 🎮 Giới thiệu
Trong “CONTRA SHOOTER” người chơi hoá thân thành chiến binh đơn độc, bắn hạ kẻ địch, thu thập các vật phẩm để vượt qua cấp độ. Sau khi mùi hương toả ra chạm đến vùng "kích hoạt" thì kẻ địch sẽ truy lùng theo dấu vết và tấn công người chơi 🔫. 

### 🎯Mục tiêu
Triển khai và so sánh bốn thuật toán tìm đường gồm **BFS**, **A\***, **Beam Search** và **Backtracking** trong bối cảnh trò chơi 2D. Các thuật toán này sẽ được dùng để giúp "enemy" xác định đường đi đến vị trí của người chơi trên bản đồ dạng lưới (grid-based map), né tránh chướng ngại vật và tối ưu hóa thời gian phản hồi. Cụ thể, **BFS** được sử dụng để tìm đường ngắn nhất một cách toàn diện, **A\*** tận dụng heuristic để tăng tốc tìm kiếm trong không gian lớn, **Beam Search** giới hạn số hướng mở rộng nhằm tăng hiệu suất với độ chính xác chấp nhận được, và **Backtracking** hỗ trợ trong các tình huống cần quay lui, như khi rơi vào ngõ cụt hoặc cần tính toán các phương án thay thế. Mục tiêu là giúp "AI" trong game di chuyển một cách thông minh và hợp lý, đồng thời kiểm tra xem các thuật toán này có hoạt động hiệu quả ra sao khi áp dụng vào môi trường chơi game thực tế, nơi mọi thứ diễn ra liên tục và cần phản hồi nhanh.

### 📦 Cấu trúc thư mục & thành phần
- Hai cấp độ mẫu (`level1.csv`, `level2.csv`)  
- Hệ thống nút bấm (button)
- Cấu hình trạng thái toàn cục trong `setting.py`  
- Âm thanh các hành động trong `audio/`  
- Đồ họa game trong `img/`  
- Thuật toán tìm đường cho "enemy" trong `algorithm.py`  
---

## CÁC THUẬT TOÁN ĐƯỢC SỬ DỤNG

### BFS (Breadth-First Search)
- **Mô tả:** Mở rộng đều các ô lân cận theo từng “lớp” trên bản đồ lưới, đảm bảo tìm ra đường đi ngắn nhất (khi mọi bước có chi phí như nhau).  
- **Ưu điểm:**  
  - Luôn tìm đường ngắn nhất.  
  - Cài đặt đơn giản.  
- **Nhược điểm:**  
  - Tiêu tốn nhiều bộ nhớ khi bản đồ lớn.  
  - Chậm nếu maze phức tạp.  

### A* (A-Star)
- **Mô tả:** Dùng hàm f(n) = g(n) + h(n) với h(n) để ưu tiên ô gần đích, giảm số nút cần duyệt.
- **Ưu điểm:**  
  - Tìm đường gần hoặc đúng tối ưu nhanh hơn BFS.
  - Linh hoạt chọn heuristic.
- **Nhược điểm:**  
  - Hiệu quả phụ thuộc vào chất lượng heuristic.
  - Còn cần nhiều bộ nhớ nếu map rất lớn.

### BEAM SEARCH
- **Mô tả:** Mỗi bước chỉ giữ lại k đường dẫn tốt nhất (beam width), cắt bớt những hướng kém khả thi để tiết kiệm thời gian.
- **Ưu điểm:**  
  - Rất nhanh, phù hợp real-time.
  - Tiết kiệm bộ nhớ.
- **Nhược điểm:**  
  - Không đảm bảo tìm được đường ngắn nhất nếu k quá nhỏ.

### BACKTRACKING
- **Mô tả:** Thử lần lượt các bước đi, nếu rơi vào dead-end thì quay lui (backtrack) và thử hướng khác.
- **Ưu điểm:**  
  - Tìm mọi lời giải khả thi.
  - Đảm bảo tìm ra đường đi nếu có.
- **Nhược điểm:**  
  - Rất chậm, không phù hợp real-time bản đồ lớn.
---

## SO SÁNH CÁC THUẬT TOÁN
Để đánh giá hiệu quả của bốn thuật toán tìm đường **BFS**, **A\***, **Beam Search** và **Backtracking** chúng ta sẽ xem xét cách chúng hoạt động trên hai cấp độ của trò chơi: `level1.csv` và `level1.csv`. Mỗi cấp độ có đặc điểm khác nhau về độ phức tạp của bản đồ, từ đó giúp làm rõ ưu và nhược điểm của từng thuật toán trong môi trường game thực tế.

### ✨ GIF cho level 1
- **BFS (Breadth-First Search)**

![BFS trên Level 1](assets/BFS_Level1.gif)

- **A\* (A-Star)**

![A* trên Level 1](assets/AStar_Level1.gif)

- **BEAM SEARCH**

![Beam Search trên Level 1](assets/BeamSearch_Level1.gif)

- **BACKTRACKING**

![Backtracking trên Level 1](assets/Backtracking_Level1.gif)


### ✨ GIF cho level 2
- **BFS (Breadth-First Search)**

![BFS trên Level 2](assets/BFS_Level2.gif)

- **A\* (A-Star)**

![A* trên Level 2](assets/AStar_Level2.gif)

- **BEAM SEARCH**

![Beam Search trên Level 1](assets/BeamSearch_Level2.gif)

- **BACKTRACKING**

![Backtracking trên Level 1](assets/Backtracking_Level2.gif)

### ✨ Bảng đánh giá thực nghiệm

| Thuật toán   | Thời gian tìm kiếm                       | Tính tối ưu                                                                            | Sử dụng bộ nhớ      | Tính đầy đủ                                        | Hành vi của kẻ địch                                                                                                                                               |
|--------------|------------------------------------------|----------------------------------------------------------------------------------------|---------------------|----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A*           | Trung bình, có thể gây trễ trong level 2 | Đảm bảo tìm được đường đi tốt nhất                                                     | Trung bình đến cao  | Có                                                 | Di chuyển hiệu quả, tìm đường ngắn nhất                                                                                                                           |
| BFS          | Trung bình, có thể gây trễ trong level 2 | Tìm được đường đi rất tốt, gần tối ưu                                                  | Cao                 | Có                                                 | Di chuyển không có định hướng rõ ràng, mở rộng tìm kiếm đều các phía. Đảm bảo đường đi ít bước nhất nhưng thiếu sự thông minh với cấu trúc map phức tạp ở level 2 |
| Beam Search  | Ngắn                                     | Đường đi có thể không tốt hoặc không hiệu quả nhưng vẫn đủ đẻ kẻ địch di chuyển hợp lý | Thấp đến trung bình | Không                                              | Phản ứng nhanh. Đường đi khá hợp lý nhúng không đảm bảo tối ưu, có thể bỏ lỡ đường đi tốt hơn                                                                     |
| Backtracking | Cao đến rất cao                          | Đường đi có thể không tốt                                                              | Trung bình đến cao  | Có thể tìm thấy đường đi nằm trong giới hạn đã đặt | Cho hiệu suất ổn định và đường đi hợp lí. Thiếu sự thông minh với cấu trúc map phức tạp ở level 2                                                                 |

Dựa trên đặc điểm của trò chơi và phân tích các thuật toán, sắp xếp mức độ phù hợp và hiệu quả của thuật toán khi áp dụng vào việc điều khiển kẻ địch trong game theo thứ tự như sau:
- **Beam Search**: Cân bằng tốt nhất giữa tốc độ tìm kiếm và chất lượng đường đi. Phản ứng nhanh của kẻ địch và hành vi di chuyển khá tự nhiên. 

- **A\***: Tìm đường đi tối ưu nhất với hành vi di chuyển hiệu quả. Có thể hơi chậm hơn Beam Search trên map có cấu trúc phức tạp như level 2.

- **Backtracking Search**: Cho hiệu suất ổn định và đường đi hợp lý, tuy nhiên hiệu năng có thể giảm trên map phức tạp như level 2. 

- **BFS**: Đơn giản, đảm bảo tìm đường ít bước nhất. Tuy nhiên, khám phá không định hướng, có thể chậm và tốn bộ nhớ hơn.
---

## Kết luận
Qua việc triển khai và so sánh bốn thuật toán tìm đường trong **CONTRASHOOTER**:
- **Beam Search** là lựa chọn tốt nhất cho môi trường game thời gian thực nhờ tốc độ nhanh và hành vi tự nhiên.

- **A\*** phù hợp khi cần đường đi tối ưu, nhưng có thể chậm hơn trên bản đồ phức tạp.

- **BFS** và **Backtracking** phù hợp cho các tình huống đơn giản hoặc khi cần đảm bảo tính đầy đủ, nhưng không tối ưu cho hiệu suất.
