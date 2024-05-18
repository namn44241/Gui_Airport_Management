from flask import Flask, render_template, request, redirect, url_for, render_template_string
import pyodbc
from datetime import datetime

app = Flask(__name__)

# Thông tin kết nối
dsn = 'QuanLiSanBay'
cnxn = pyodbc.connect(f'DSN={dsn}')
cursor = cnxn.cursor()
                           
@app.route('/test_connection')
def test_connection():
    try:
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"
        cursor.execute(query)
        tables = cursor.fetchall()
        return f"Kết nối thành công! Danh sách các bảng: {tables}"
    except Exception as e:
        return f"Kết nối thất bại: {str(e)}"
    
@app.route('/')
def index():
    flight_info = []
    plane_info = []
    booking_info = []
    aircraft_info = []
    customer_info = []
    employee_info = []
    schedule_info = []
    assignment_info = []

    # Lấy danh sách chuyến bay từ cơ sở dữ liệu
    query = "SELECT MaChuyenBay, TenSanBayDi, TenSanBayDen, GioDi, GioDen FROM ChuyenBay"
    cursor.execute(query)
    flight_info = [row for row in cursor.fetchall()]

    # Lấy danh sách loại máy bay từ cơ sở dữ liệu
    query = "SELECT MaLoai, HangSanXuat FROM LoaiMayBay"
    cursor.execute(query)
    aircraft_info = [row for row in cursor.fetchall()]

    # Lấy danh sách thông tin đặt chỗ từ cơ sở dữ liệu
    query = "SELECT KhachHang.MaKH, NgayDi, ChuyenBay.MaChuyenBay FROM DatCho JOIN KhachHang ON DatCho.MaKH = KhachHang.MaKH JOIN ChuyenBay ON DatCho.MaChuyenBay = ChuyenBay.MaChuyenBay"
    cursor.execute(query)
    booking_info = [row for row in cursor.fetchall()]

    # Lấy danh sách khách hàng từ cơ sở dữ liệu
    query = "SELECT MaKH FROM KhachHang"
    cursor.execute(query)
    customer_list = [row for row in cursor.fetchall()]

    # Lấy danh sách chuyến bay từ cơ sở dữ liệu
    query = "SELECT MaChuyenBay FROM ChuyenBay"
    cursor.execute(query)
    flight_list = [row for row in cursor.fetchall()]

    return render_template('index.html', flight_info=flight_info, plane_info=plane_info, booking_info=booking_info,
                       aircraft_info=aircraft_info, customer_info=customer_info, employee_info=employee_info,
                       schedule_info=schedule_info, assignment_info=assignment_info,
                       customer_list=customer_list, flight_list=flight_list)

@app.route('/them_cb', methods=['POST'])
def them_cb():
    flight_id = request.form['flight-id']
    departure_airport = request.form['departure-airport']
    arrival_airport = request.form['arrival-airport']
    departure_time = datetime.strptime(request.form['departure-time'], "%Y-%m-%dT%H:%M")
    arrival_time = datetime.strptime(request.form['arrival-time'], "%Y-%m-%dT%H:%M")

    query = "INSERT INTO ChuyenBay (MaChuyenBay, TenSanBayDi, TenSanBayDen, GioDi, GioDen) VALUES (?, ?, ?, ?, ?)"
    values = (flight_id, departure_airport, arrival_airport, departure_time, arrival_time)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('index'))

@app.route('/sua_cb', methods=['POST'])
def sua_cb():
    flight_id = request.form['flight-id']
    departure_airport = request.form['departure-airport']
    arrival_airport = request.form['arrival-airport']
    departure_time = datetime.strptime(request.form['departure-time'], "%Y-%m-%dT%H:%M")
    arrival_time = datetime.strptime(request.form['arrival-time'], "%Y-%m-%dT%H:%M")
    query = "UPDATE ChuyenBay SET TenSanBayDi = ?, TenSanBayDen = ?, GioDi = ?, GioDen = ? WHERE MaChuyenBay = ?"
    values = (departure_airport, arrival_airport, departure_time, arrival_time, flight_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('index'))

@app.route('/xoa_cb/<flight_id>', methods=['POST'])
def xoa_cb(flight_id):
    query = "DELETE FROM ChuyenBay WHERE MaChuyenBay = ?"
    cursor.execute(query, (flight_id,))
    cnxn.commit()
    return redirect(url_for('index'))

# Các hàm xử lý cho quản lý loại máy bay
@app.route('/them_loai_mb', methods=['POST'])
def them_loai_mb():
    plane_type_id = request.form['plane-type-id']
    manufacturer = request.form['manufacturer']
    query = "INSERT INTO LoaiMayBay (MaLoai, HangSanXuat) VALUES (?, ?)"
    values = (plane_type_id, manufacturer)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('index', section='aircraft-types'))

@app.route('/sua_loai_mb', methods=['POST'])
def sua_loai_mb():
    plane_type_id = request.form['plane-type-id']
    manufacturer = request.form['manufacturer']
    query = "UPDATE LoaiMayBay SET HangSanXuat = ? WHERE MaLoai = ?"
    values = (manufacturer, plane_type_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('index', section='aircraft-types'))

@app.route('/xoa_loai_mb/<plane_type_id>', methods=['POST'])
def xoa_loai_mb(plane_type_id):
    query = "DELETE FROM LoaiMayBay WHERE MaLoai = ?"
    cursor.execute(query, (plane_type_id,))
    cnxn.commit()
    return redirect(url_for('index', section='aircraft-types'))


# Hàm kiểm tra tồn tại khách hàng
def check_customer_exists(customer_id):
    query = "SELECT COUNT(*) FROM KhachHang WHERE MaKH = ?"
    cursor.execute(query, (customer_id,))
    count = cursor.fetchone()[0]
    return count > 0

# Hàm kiểm tra tồn tại chuyến bay
def check_flight_exists(flight_id):
    query = "SELECT COUNT(*) FROM ChuyenBay WHERE MaChuyenBay = ?"
    cursor.execute(query, (flight_id,))
    count = cursor.fetchone()[0]
    return count > 0

# Hàm kiểm tra tồn tại lịch bay
def check_flight_schedule_exists(flight_id, departure_date):
    query = "SELECT COUNT(*) FROM LichBay WHERE MaChuyenBay = ? AND NgayDi = ?"
    cursor.execute(query, (flight_id, departure_date))
    count = cursor.fetchone()[0]
    return count > 0

@app.route('/get_departure_date/<customer_id>/<flight_id>', methods=['GET'])
def get_departure_date(customer_id, flight_id):
    query = "SELECT NgayDi FROM DatCho WHERE MaKH = ? AND MaChuyenBay = ?"
    cursor.execute(query, (customer_id, flight_id))
    result = cursor.fetchone()
    if result:
        departure_date = result[0].strftime('%Y-%m-%d')
        return {'departure_date': departure_date}
    else:
        return {'departure_date': ''}
    
@app.route('/them_dat_cho', methods=['POST'])
def them_dat_cho():
    customer_id = request.form['customer-id']
    departure_date = request.form['departure-date']
    flight_id = request.form['flight-id']

    # Kiểm tra xem MaKH có tồn tại trong bảng KhachHang hay không
    if not check_customer_exists(customer_id):
        return "Mã khách hàng không hợp lệ"

    # Kiểm tra xem MaChuyenBay có tồn tại trong bảng ChuyenBay hay không
    if not check_flight_exists(flight_id):
        return "Mã chuyến bay không hợp lệ"

    # Kiểm tra xem MaChuyenBay có tồn tại trong bảng LichBay hay không với NgayDi
    if not check_flight_schedule_exists(flight_id, departure_date):
        return "Mã chuyến bay không tồn tại trong lịch bay với ngày đi đã chọn"

    # Thực hiện thêm thông tin đặt chỗ vào cơ sở dữ liệu
    query = "INSERT INTO DatCho (MaKH, NgayDi, MaChuyenBay) VALUES (?, ?, ?)"
    values = (customer_id, departure_date, flight_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))

@app.route('/sua_dat_cho', methods=['POST'])
def sua_dat_cho():
    customer_id = request.form['customer-id']
    departure_date = request.form['departure-date']
    flight_id = request.form['flight-id']

    # Kiểm tra xem MaKH có tồn tại trong bảng KhachHang hay không
    if not check_customer_exists(customer_id):
        return "Mã khách hàng không hợp lệ"

    # Kiểm tra xem MaChuyenBay có tồn tại trong bảng ChuyenBay hay không
    if not check_flight_exists(flight_id):
        return "Mã chuyến bay không hợp lệ"

    # Kiểm tra xem MaChuyenBay có tồn tại trong bảng LichBay hay không với NgayDi
    if not check_flight_schedule_exists(flight_id, departure_date):
        return "Mã chuyến bay không tồn tại trong lịch bay với ngày đi đã chọn"

    query = "UPDATE DatCho SET MaChuyenBay = ?, NgayDi = ? WHERE MaKH = ?"
    values = (flight_id, departure_date, customer_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))

@app.route('/xoa_dat_cho/<customer_id>/<departure_date>/<flight_id>', methods=['POST'])
def xoa_dat_cho(customer_id, departure_date, flight_id):
    # Thực hiện xóa thông tin đặt chỗ từ cơ sở dữ liệu
    query = "DELETE FROM DatCho WHERE MaKH = ? AND NgayDi = ? AND MaChuyenBay = ?"
    values = (customer_id, departure_date, flight_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))

@app.route('/them_mb', methods=['POST'])
def them_mb():
    plane_id = request.form['plane-id']
    plane_type_id = request.form['plane-type-id']
    seat_quantity = request.form['seat-quantity']

    # Thực hiện các thao tác thêm thông tin máy bay vào cơ sở dữ liệu ở đây
    # ...

    return redirect(url_for('index'))  # Hoặc chuyển hướng đến trang cần thiết

@app.route('/sua_mb', methods=['POST'])
def sua_mb():
    plane_id = request.form['plane-id']
    plane_type_id = request.form['plane-type-id']
    seat_quantity = request.form['seat-quantity']

    # Thực hiện các thao tác sửa thông tin máy bay trong cơ sở dữ liệu ở đây
    # ...

    return redirect(url_for('index'))  # Hoặc chuyển hướng đến trang cần thiết

@app.route('/xoa_mb/<plane_id>', methods=['DELETE'])
def xoa_mb(plane_id):
    # Thực hiện các thao tác xóa thông tin máy bay từ cơ sở dữ liệu ở đây
    # ...

    return redirect(url_for('index'))  # Hoặc chuyển hướng đến trang cần thiết

@app.route('/them_kh', methods=['POST'])
def them_kh():
    customer_id = request.form['customer-id']
    customer_name = request.form['customer-name']
    customer_phone = request.form['customer-phone']
    customer_address = request.form['customer-address']

    query = "INSERT INTO KhachHang (MaKH, TenKH, SDT, DiaChi) VALUES (?, ?, ?, ?)"
    values = (customer_id, customer_name, customer_phone, customer_address)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi thêm

@app.route('/sua_kh', methods=['POST'])
def sua_kh():
    customer_id = request.form['customer-id']
    customer_name = request.form['customer-name']
    customer_phone = request.form['customer-phone']
    customer_address = request.form['customer-address']

    query = "UPDATE KhachHang SET TenKH = ?, SDT = ?, DiaChi = ? WHERE MaKH = ?"
    values = (customer_name, customer_phone, customer_address, customer_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi sửa

@app.route('/xoa_kh/<customer_id>', methods=['DELETE'])
def xoa_kh(customer_id):
    query = "DELETE FROM KhachHang WHERE MaKH = ?"
    cursor.execute(query, (customer_id,))
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi xóa

@app.route('/them_nv', methods=['POST'])
def them_nv():
    employee_id = request.form['employee-id']
    employee_name = request.form['employee-name']
    employee_phone = request.form['employee-phone']
    employee_address = request.form['employee-address']

    query = "INSERT INTO NhanVien (MaNV, TenNV, SDT, DiaChi) VALUES (?, ?, ?, ?)"
    values = (employee_id, employee_name, employee_phone, employee_address)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi thêm

@app.route('/sua_nv/<employee_id>', methods=['POST'])
def sua_nv(employee_id):
    employee_name = request.form['employee-name']
    employee_phone = request.form['employee-phone']
    employee_address = request.form['employee-address']

    query = "UPDATE NhanVien SET TenNV = ?, SDT = ?, DiaChi = ? WHERE MaNV = ?"
    values = (employee_name, employee_phone, employee_address, employee_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi sửa

@app.route('/xoa_nv/<employee_id>', methods=['DELETE'])
def xoa_nv(employee_id):
    query = "DELETE FROM NhanVien WHERE MaNV = ?"
    cursor.execute(query, (employee_id,))
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi xóa

@app.route('/them_lich', methods=['POST'])
def them_lich():
    schedule_id = request.form['schedule-id']
    flight_id = request.form['flight-id']
    departure_date = request.form['departure-date']
    arrival_date = request.form['arrival-date']

    query = "INSERT INTO LichBay (MaLichBay, MaCB, NgayDi, NgayDen) VALUES (?, ?, ?, ?)"
    values = (schedule_id, flight_id, departure_date, arrival_date)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi thêm

@app.route('/sua_lich/<schedule_id>', methods=['POST'])
def sua_lich(schedule_id):
    flight_id = request.form['flight-id']
    departure_date = request.form['departure-date']
    arrival_date = request.form['arrival-date']

    query = "UPDATE LichBay SET MaCB = ?, NgayDi = ?, NgayDen = ? WHERE MaLichBay = ?"
    values = (flight_id, departure_date, arrival_date, schedule_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi sửa

@app.route('/xoa_lich/<schedule_id>', methods=['DELETE'])
def xoa_lich(schedule_id):
    query = "DELETE FROM LichBay WHERE MaLichBay = ?"
    cursor.execute(query, (schedule_id,))
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi xóa

@app.route('/them_phan_cong', methods=['POST'])
def them_phan_cong():
    employee_id = request.form['employee-id']
    schedule_id = request.form['schedule-id']

    query = "INSERT INTO PhanCong (MaNV, MaLichBay) VALUES (?, ?)"
    values = (employee_id, schedule_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi thêm

@app.route('/sua_phan_cong/<employee_id>/<schedule_id>', methods=['POST'])
def sua_phan_cong(employee_id, schedule_id):
    new_employee_id = request.form['new-employee-id']
    new_schedule_id = request.form['new-schedule-id']

    query = "UPDATE PhanCong SET MaNV = ?, MaLichBay = ? WHERE MaNV = ? AND MaLichBay = ?"
    values = (new_employee_id, new_schedule_id, employee_id, schedule_id)
    cursor.execute(query, values)
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi sửa

@app.route('/xoa_phan_cong/<employee_id>/<schedule_id>', methods=['DELETE'])
def xoa_phan_cong(employee_id, schedule_id):
    query = "DELETE FROM PhanCong WHERE MaNV = ? AND MaLichBay = ?"
    cursor.execute(query, (employee_id, schedule_id))
    cnxn.commit()

    return redirect(url_for('index'))  # Chuyển hướng sau khi xóa

if __name__ == '__main__':
    app.run(debug=True)