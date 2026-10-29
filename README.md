# LensAI – Virtual Try-On

## Giới thiệu dự án

**LensAI – Virtual Try-On** là ứng dụng thử kính trực tuyến sử dụng xử lý ảnh và nhận diện khuôn mặt theo thời gian thực.

Hệ thống cho phép người dùng sử dụng camera để thử các mẫu kính trực tiếp trên khuôn mặt, thay đổi mẫu kính và màu sắc, đồng thời phân tích một số đặc điểm khuôn mặt để đưa ra điểm đánh giá mức độ phù hợp của từng mẫu kính.

Ứng dụng được xây dựng bằng **Python, Streamlit, OpenCV và MediaPipe**.

## 1. Chức năng chính

### Cửa hàng kính

- Hiển thị danh sách các mẫu kính.
- Hiển thị tên, loại, phong cách, màu sắc và giá sản phẩm.
- Lọc kính theo loại.
- Chọn một hoặc nhiều mẫu kính để thử.
- Chọn ngẫu nhiên các mẫu kính.
- Lưu sản phẩm vào danh sách yêu thích.

### Thử kính trực tuyến

- Sử dụng camera máy tính theo thời gian thực.
- Nhận diện các điểm đặc trưng trên khuôn mặt bằng MediaPipe.
- Đặt hình ảnh kính lên đúng vị trí khuôn mặt.
- Tự động điều chỉnh kích thước và góc kính theo khuôn mặt.
- Thay đổi mẫu kính bằng thao tác nháy mắt.
- Thay đổi màu kính bằng thao tác nghiêng đầu.

### Phân tích khuôn mặt

Hệ thống phân tích một số đặc điểm như:

- Tỉ lệ chiều rộng và chiều cao khuôn mặt.
- Độ rộng hàm.
- Độ rộng vùng trán.
- Khoảng cách giữa hai mắt.
- Tông da ước lượng từ hình ảnh camera.

Khuôn mặt được phân loại thành một số dạng:

- Oval.
- Tròn.
- Vuông.
- Dài.
- Trái tim.

## 2. Đánh giá mức độ phù hợp của kính

Hệ thống sử dụng các quy tắc được định nghĩa trong chương trình để tính điểm phù hợp giữa:

- Dáng khuôn mặt.
- Kiểu kính.
- Màu kính.
- Tông da.
- Khoảng cách mắt.

Mỗi mẫu kính được đánh giá theo thang điểm:

**1 – 10**

Sau khi thử nhiều mẫu, hệ thống có thể:

- Lưu điểm từng mẫu kính.
- Xếp hạng các mẫu đã thử.
- Hiển thị Top 5 mẫu phù hợp.
- Đề xuất mẫu kính có điểm cao nhất.

> Điểm số trong phiên bản hiện tại được tính dựa trên các quy tắc được định nghĩa trong chương trình, không phải mô hình Machine Learning được huấn luyện từ dữ liệu người dùng.

## 3. Danh sách yêu thích

Người dùng có thể:

- Lưu mẫu kính yêu thích.
- Xem lại danh sách đã lưu.
- Chọn mẫu kính yêu thích để thử.
- Thử tất cả các mẫu đã lưu.
- Xóa sản phẩm khỏi danh sách yêu thích.

## 4. Quản lý mẫu kính

Ứng dụng có khu vực dành cho quản trị viên.

Quản trị viên có thể:

- Đăng nhập khu vực quản trị.
- Upload một hoặc nhiều ảnh kính.
- Hỗ trợ các định dạng PNG, JPG, JPEG, WEBP và GIF.
- Đặt tên sản phẩm.
- Nhập giá sản phẩm.
- Thêm mẫu kính mới vào cửa hàng.
- Quản lý các mẫu kính đã được thêm.

Ảnh PNG có nền trong suốt được khuyến nghị để đạt hiệu quả tốt hơn khi đặt kính lên khuôn mặt.

## 5. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python |
| Giao diện | Streamlit |
| Xử lý hình ảnh | OpenCV |
| Nhận diện khuôn mặt | MediaPipe |
| Xử lý dữ liệu | NumPy |
| Xử lý ảnh | Pillow |
| Dữ liệu sản phẩm | JSON / File System |

## 6. Cấu trúc chính

```text
virtual_glasses/
│
├── app.py
├── generate_assets.py
├── custom_meta.json
├── requirements.txt
└── images/
```

### `app.py`

File chính của ứng dụng, bao gồm:

- Giao diện Streamlit.
- Danh mục kính.
- Danh sách yêu thích.
- Camera thử kính.
- MediaPipe Face Landmark.
- Phân tích đặc điểm khuôn mặt.
- Tính điểm phù hợp.
- Quản lý upload sản phẩm.

### `generate_assets.py`

Tạo một số hình ảnh kính mẫu phục vụ quá trình thử nghiệm.

### `custom_meta.json`

Lưu thông tin bổ sung của các mẫu kính được upload.

### `requirements.txt`

Các thư viện chính:

```text
streamlit
opencv-python
numpy
mediapipe
Pillow
```

## 7. Phạm vi hiện tại

Phiên bản hiện tại tập trung vào:

- Virtual Try-On bằng camera.
- Nhận diện landmark khuôn mặt.
- Overlay kính theo thời gian thực.
- Điều khiển bằng cử chỉ đơn giản.
- Phân tích đặc điểm khuôn mặt.
- Chấm điểm và xếp hạng kính.
- Quản lý danh mục kính cơ bản.

Các chức năng giỏ hàng và mua hàng trong giao diện hiện tại chủ yếu phục vụ mô phỏng trải nghiệm và chưa phải một hệ thống thanh toán thương mại điện tử hoàn chỉnh.

## 8. Hướng phát triển

Ứng dụng có thể được mở rộng với:

- Cải thiện độ chính xác khi đặt kính lên khuôn mặt.
- Huấn luyện mô hình gợi ý kính từ dữ liệu thực tế.
- Quản lý tài khoản người dùng.
- Lưu lịch sử thử kính.
- Giỏ hàng và thanh toán thực tế.
- Quản lý sản phẩm bằng cơ sở dữ liệu.
- Triển khai ứng dụng trên môi trường Cloud.
