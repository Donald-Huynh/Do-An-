# Import thư viện
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from itertools import repeat
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd 
pd.set_option('mode.chained_assignment', None)
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageTk 

# Biến toàn cục để phân trang
current_page = 1    
page_size = 30    

#___________________________________________________ Hàm xử lý sự kiện _______________________________________________________________________
# Hàm đọc tệp CSV
def load_csv(file_path):
    """Đọc tệp CSV từ đường dẫn và trả về một DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc tệp CSV: {e}")
        return None
# Hàm hiển thị dữ liệu phân trang
def open_file():
    global data, current_page
    file_selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_selected:
        data = load_csv(file_selected)
        if data is not None:
            current_page = 1  # Reset về trang đầu tiên
            display_paginated_data()

# Hàm nhập file
def open_file():
    global data, file_selected
    file_selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_selected:
        new_data = load_csv(file_selected)
        if new_data is not None:
            data = new_data  # Cập nhật biến toàn cục
            messagebox.showinfo("Thông báo", f"Đã chọn tệp: {file_selected}")
            display_data()  # Hiển thị dữ liệu mới
        else:
            messagebox.showerror("Lỗi", "Không thể tải dữ liệu từ tệp được chọn.")
    else:
        messagebox.showwarning("Cảnh báo", "Bạn chưa chọn file nào!")

# Hàm sắp xếp treeview
def sort_treeview_column(column, reverse):
    """Sắp xếp Treeview theo cột được chọn."""
    global data, tree
    # Lấy dữ liệu của cột
    try:
        if column in data.columns:
            # Sắp xếp DataFrame theo cột
            sorted_data = data.sort_values(by=column, ascending=not reverse)

            # Cập nhật lại Treeview
            update_treeview(sorted_data)

            # Đảo trạng thái sắp xếp cho lần nhấp tiếp theo
            tree.heading(column, command=lambda: sort_treeview_column(column, not reverse))
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể sắp xếp cột '{column}': {e}")

# Hàm tìm kiếm dữ liệu
def search_data():
    """Tìm kiếm dữ liệu dựa trên từ khóa."""
    global data, tree

    keyword = search_entry.get().strip()  # Lấy từ khóa từ ô nhập liệu

    if not keyword:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
        return

    try:
        # Lọc dữ liệu: kiểm tra từ khóa có xuất hiện trong bất kỳ cột nào
        filtered_data = data[data.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]

        # Cập nhật TreeView với dữ liệu tìm kiếm
        update_treeview(filtered_data)
        messagebox.showinfo("Thông báo", f"Tìm thấy {len(filtered_data)} dòng chứa từ khóa '{keyword}'!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tìm kiếm dữ liệu: {e}")

# Hàm hiển thị treeview
def display_data():
    """Hiển thị dữ liệu hiện tại trong bảng Treeview với thanh cuộn."""
    global tree, column_combobox
    # Cập nhật danh sách cột trong Combobox
    if data is not None and not data.empty:
        column_combobox['values'] = list(data.columns)
    """Hiển thị dữ liệu hiện tại trong bảng Treeview với thanh cuộn."""
    global tree
    # Xóa các widget cũ trong frame_display
    for widget in frame_display.winfo_children():
        widget.destroy()
    # Tạo khung chứa Treeview và thanh cuộn
    tree_frame = tk.Frame(frame_display)
    tree_frame.pack(fill="both", expand=True)
    # Tạo Treeview
    columns = list(data.columns)
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    # Thêm thanh cuộn dọc
    scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)
    # Thêm thanh cuộn ngang
    scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)
    # Đặt Treeview vào khung
    tree.pack(fill="both", expand=True)
    # Thiết lập tiêu đề cột
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(c, False))
        tree.column(col, width=100)
    # Thêm dữ liệu vào Treeview
    for _, row in data.iterrows():
        tree.insert("", tk.END, values=row.tolist())

# Hàm lọc dữ liệu
def apply_filter():
    """Lọc dữ liệu dựa trên các điều kiện nhập từ UI."""
    global data, tree
    # Lấy giá trị từ các widget
    column = column_combobox.get()
    condition = condition_combobox.get()
    value = value_entry.get()

    if not column or not condition or not value:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin để lọc!")
        return

    try:
        # Chuyển đổi giá trị nếu cần
        if value.replace('.', '', 1).isdigit():
            value = float(value)

        # Lọc dữ liệu
        if condition == "=":
            filtered_data = data[data[column] == value]
        elif condition == ">":
            filtered_data = data[data[column] > value]
        elif condition == "<":
            filtered_data = data[data[column] < value]
        elif condition == "contains":
            filtered_data = data[data[column].astype(str).str.contains(value, case=False)]
        else:
            messagebox.showwarning("Lỗi", "Điều kiện không hợp lệ!")
            return

        # Cập nhật Treeview với dữ liệu đã lọc
        update_treeview(filtered_data)
        messagebox.showinfo("Thông báo", "Dữ liệu đã được lọc!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lọc dữ liệu: {e}")

# Hàm thêm dữ liệu
def add_new_data():
    """Hiển thị cửa sổ để thêm dữ liệu mới vào DataFrame."""
    global data, tree

    if data is None or data.empty:
        messagebox.showwarning("Cảnh báo", "Không có dữ liệu để thêm! Hãy tải tệp CSV trước.")
        return

    # Hiển thị cửa sổ nhập liệu
    add_window = tk.Toplevel(root)
    add_window.title("Thêm dữ liệu mới")
    add_window.geometry("500x500")

    # Tạo Canvas và khung cuộn
    canvas = tk.Canvas(add_window)
    scrollbar = ttk.Scrollbar(add_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Cấu hình khung cuộn
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Đặt Canvas và Scrollbar vào cửa sổ
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Tạo các trường nhập liệu trong khung cuộn
    entry_widgets = {}
    for idx, col in enumerate(data.columns):
        tk.Label(scrollable_frame, text=col, font=("Arial", 10, "bold")).grid(row=idx, column=0, padx=5, pady=5)
        entry = tk.Entry(scrollable_frame, font=("Arial", 10))
        entry.grid(row=idx, column=1, padx=5, pady=5)
        entry_widgets[col] = entry

    def save_new_data():
        """Lưu dữ liệu mới vào DataFrame và cập nhật Treeview."""
        try:
            # Thu thập dữ liệu từ các trường nhập
            new_row = {col: entry.get() for col, entry in entry_widgets.items()}

            # Chuyển đổi giá trị số nếu có
            for col in new_row:
                if new_row[col].replace('.', '', 1).isdigit():
                    new_row[col] = float(new_row[col])

            # Thêm dòng mới vào DataFrame
            global data
            new_df = pd.DataFrame([new_row])
            data = pd.concat([data, new_df], ignore_index=True)

            # Cập nhật lại Treeview
            update_treeview(data)

            # Lưu lại tệp nếu đã chọn
            if file_selected:
                data.to_csv(file_selected, index=False)

            # Thông báo và đóng cửa sổ
            messagebox.showinfo("Thông báo", "Dữ liệu đã được thêm thành công!")
            add_window.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm dữ liệu: {e}")

    # Nút lưu dữ liệu
    tk.Button(scrollable_frame, text="Lưu", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=save_new_data).grid(row=len(data.columns), column=0, columnspan=2, pady=10)

# Hàm cập nhật treeview sau khi lọc
def update_treeview(filtered_data):
    """Cập nhật Treeview với dữ liệu đã lọc."""
    global tree

    # Xóa tất cả dữ liệu cũ trong Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Thêm dữ liệu mới từ DataFrame vào Treeview
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            tree.insert("", tk.END, values=row.tolist())
    else:
        messagebox.showinfo("Thông báo", "Không có dữ liệu khớp với điều kiện lọc!")


# Hàm chỉnh sửa dữ liệu
def edit_row():
    """Chỉnh sửa dữ liệu trong Treeview và DataFrame."""
    global tree, data  # Sử dụng biến toàn cục

    try:
        # Lấy dòng được chọn trong Treeview
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần chỉnh sửa!")
            return

        # Lấy giá trị của dòng được chọn
        item = selected_items[0]
        row_values = tree.item(item, 'values')

        # Hiển thị hộp thoại chỉnh sửa
        edit_window = tk.Toplevel(root)
        edit_window.title("Chỉnh sửa dữ liệu")
        edit_window.geometry("400x400")

        # Tạo Canvas và thanh cuộn
        canvas = tk.Canvas(edit_window)
        scrollbar = tk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Cấu hình thanh cuộn
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Đặt vị trí của Canvas và Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tạo các trường nhập liệu cho mỗi cột trong khung cuộn
        entry_widgets = []
        for idx, col in enumerate(data.columns):
            tk.Label(scrollable_frame, text=col, font=("Arial", 10, "bold")).grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(scrollable_frame, font=("Arial", 10))
            entry.insert(0, row_values[idx])
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entry_widgets.append(entry)


        # Hàm cập nhật dữ liệu
        def update_data():
            try:
                # Lấy dữ liệu mới từ các trường nhập liệu
                new_values = [entry.get() for entry in entry_widgets]

                # Cập nhật Treeview
                tree.item(item, values=new_values)

                # Cập nhật DataFrame
                index_to_update = data[
                    (data == pd.Series(row_values, index=data.columns)).all(axis=1)
                ].index
                if not index_to_update.empty:
                    data.loc[index_to_update[0]] = new_values

                # Lưu lại tệp nếu cần
                if file_selected:
                    data.to_csv(file_selected, index=False)

                # Thông báo thành công
                messagebox.showinfo("Thông báo", "Dữ liệu đã được cập nhật và lưu thành công!")
                edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật dữ liệu: {e}")

        # Nút Lưu
        tk.Button(scrollable_frame, text="Lưu", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=update_data).grid(row=len(data.columns), column=0, columnspan=2, pady=10)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể chỉnh sửa dữ liệu: {e}")

# Hàm kiểm tra 
def check_file_selected(action):
    if not file_selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn file CSV trước!")
        return False
    return True

# Hàm xóa dòng
def delete_row():
    """Xóa dòng dữ liệu được chọn trong bảng Treeview và lưu lại vào tệp CSV."""
    global tree, data  # Sử dụng biến toàn cục

    try:
        # Kiểm tra nếu Treeview và dữ liệu tồn tại
        if not tree or data is None:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xóa!")
            return

        # Lấy các dòng được chọn trong Treeview
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần xóa!")
            return

        # Xóa từng dòng được chọn
        for item in selected_items:
            # Lấy giá trị dòng từ Treeview
            row_values = tree.item(item, 'values')
            # Xóa dòng tương ứng trong DataFrame
            data.drop(data[(data == pd.Series(row_values, index=data.columns)).all(axis=1)].index, inplace=True)
            # Xóa dòng từ Treeview
            tree.delete(item)

        # Lưu lại dữ liệu vào tệp CSV
        if file_selected:
            data.to_csv(file_selected, index=False)
            messagebox.showinfo("Thông báo", "Dữ liệu đã được lưu sau khi xóa!")
        else:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy tệp để lưu!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu: {e}")

# Phân Trang
def display_paginated_data():
    """Hiển thị dữ liệu trong TreeView theo phân trang."""
    global current_page, page_size, data, tree

    # Xóa nội dung TreeView hiện tại
    for item in tree.get_children():
        tree.delete(item)

    # Tính toán phạm vi dữ liệu cần hiển thị
    start_row = (current_page - 1) * page_size
    end_row = min(start_row + page_size, len(data))
    paginated_data = data.iloc[start_row:end_row]

    # Thêm dữ liệu của trang hiện tại vào TreeView
    for _, row in paginated_data.iterrows():
        tree.insert("", tk.END, values=row.tolist())

    # Cập nhật thông báo trạng thái trang
    update_page_status()
def go_to_next_page():
    """Chuyển sang trang tiếp theo."""
    global current_page
    if current_page * page_size < len(data):
        current_page += 1
        display_paginated_data()

def go_to_previous_page():
    """Quay lại trang trước."""
    global current_page
    if current_page > 1:
        current_page -= 1
        display_paginated_data()

def update_page_status():
    """Cập nhật trạng thái trang."""
    total_pages = (len(data) + page_size - 1) // page_size
    page_status_label.config(text=f"Trang {current_page}/{total_pages}")


#_________________________________________Hàm Biểu Đồ_________________________________________________________________________________

def country():
    if check_file_selected("Mở biểu đồ"):
        # Tính toán tỷ lệ quốc tịch
        nationality_counts = data['Nationality'].value_counts()

        # Giới hạn hiển thị top 10 quốc gia, gộp các quốc gia khác vào "Other"
        top_nationalities = nationality_counts[:10]
        other_nationalities = nationality_counts[10:].sum()
        nationality_labels = list(top_nationalities.index) + ['Other']
        nationality_sizes = list(top_nationalities.values) + [other_nationalities]

        # Tạo biểu đồ tròn
        plt.figure(figsize=(10, 8))
        plt.pie(
            nationality_sizes, 
            labels=nationality_labels, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=plt.cm.tab20.colors,  # Bảng màu đa dạng
            pctdistance=0.85,  # Vị trí phần trăm
            labeldistance=1.1  # Vị trí nhãn
        )

        # Tạo vòng tròn bên trong (tạo hiệu ứng Donut Chart)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Gắn tiêu đề
        plt.title('Tỷ lệ quốc tịch của các cầu thủ')
        plt.tight_layout()

        # Hiển thị biểu đồ
        plt.show()

def cauthu_scored():
    if check_file_selected("Mở biểu đồ"):
        # Lọc các cột liên quan và loại bỏ dữ liệu bị thiếu
        player_goals = data[['Name', 'Goals']].dropna()

        # Sắp xếp cầu thủ theo số bàn thắng giảm dần và chọn top 25
        top_players = player_goals.sort_values(by='Goals', ascending=False).head(25)

        # Chọn màu sắc khác nhau cho từng cột
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_players)))

        # Tạo biểu đồ cột với màu sắc khác nhau
        plt.figure(figsize=(14, 8))
        bars = plt.bar(top_players['Name'], top_players['Goals'], color=colors)

        # Thêm số bàn thắng trên mỗi cột
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,  # Vị trí x
                yval + 0.5,  # Vị trí y (thêm một chút khoảng cách để không bị che khuất)
                str(int(yval)),  # Số bàn thắng
                ha='center',  # Căn giữa
                va='bottom',  # Căn đáy
                fontweight='bold'  # Làm đậm số
            )

        # Gắn nhãn và tiêu đề
        plt.xticks(rotation=90, ha='center')  # Xoay tên cầu thủ để tránh chồng chéo
        plt.ylabel('Number of Goals')
        plt.title('Top 25 Cầu Thủ Ghi Bàn Nhiều Nhất')

        # Hiển thị biểu đồ
        plt.tight_layout()
        plt.show()

def age():
    if check_file_selected("Mở biểu đồ"):
        # Kiểm tra và lọc dữ liệu để đảm bảo không có giá trị bị thiếu
        data_filtered = data[['Age', 'Appearances', 'Goals']].dropna()

        # Tạo kích thước điểm dựa trên số bàn thắng
        sizes = data_filtered['Goals'] * 10  # Phóng to để rõ ràng hơn
        sizes[sizes == 0] = 20  # Đảm bảo điểm có kích thước nhỏ nhất là 20

        # Tạo biểu đồ phân tán
        plt.figure(figsize=(14, 8))
        scatter = plt.scatter(
            data_filtered['Age'], 
            data_filtered['Appearances'], 
            s=sizes,  # Kích thước điểm
            alpha=0.7, 
            c=data_filtered['Age'],  # Màu theo tuổi để nhận biết xu hướng
            cmap='viridis',  # Bảng màu
            edgecolors='k'
        )

        # Thêm thanh màu (color bar) để chú thích
        cbar = plt.colorbar(scatter)
        cbar.set_label('Age', fontsize=12)

        # Gắn nhãn trục và tiêu đề
        plt.xlabel('Age', fontsize=14)
        plt.ylabel('Number of Appearances', fontsize=14)
        plt.title('Mối quan hệ giữa tuổi và số lần thi đấu',fontweight='bold' ,fontsize=20, color='red')

        # Thêm lưới
        plt.grid(alpha=0.3)

        # Hiển thị biểu đồ
        plt.tight_layout()
        plt.show()

def quocgia_scored():
    if check_file_selected("Mở biểu đồ"):    
        # Group by Nationality and sum the Goals column
        goals_by_country = data.groupby('Nationality')['Goals'].sum().sort_values(ascending=False)

        # Select top 10 countries by goals scored for visualization
        top_10_countries = goals_by_country.head(10)

        # Plotting the data
        plt.figure(figsize=(10, 6))
        top_10_countries.plot(kind='bar', color='skyblue', edgecolor='black')

        # Adding titles and labels
        plt.title('Top 10 quốc gia theo tổng số bàn thắng ghi được', fontsize=18, color= 'red')
        plt.xlabel('Quốc gia', fontsize=12)
        plt.ylabel('Tổng số bàn thắng ghi được', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Show the plot
        plt.tight_layout()
        plt.show()

def banthang():
    if check_file_selected("Mở biểu đồ"):    
        goal_distribution = data.groupby('Club')[
            ['Goals with right foot', 'Goals with left foot', 'Headed goals']
        ].sum()

        # Plotting the stacked bar chart
        plt.figure(figsize=(14, 8))
        ax = goal_distribution.plot(kind='bar', stacked=True, 
                                    color=['#D62728', '#FF7F0E', '#17BECF'], 
                                    edgecolor='black', figsize=(14, 8))

        # Adding value annotations to each bar
        for i, club in enumerate(goal_distribution.index):
            y_offset = 0
            for col in goal_distribution.columns:
                value = goal_distribution.loc[club, col]
                if value > 0:  # Annotate only non-zero values
                    plt.text(i, y_offset + value / 2, int(value), ha='center', fontsize=8)
                    y_offset += value

        # Adding titles and labels
        plt.title('Bàn Thắng Theo Từng CLB', fontsize=16, color = 'red')
        plt.xlabel('CLB', fontsize=12)
        plt.ylabel('Số Bàn Thắng', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.legend(['Chân phải', 'Chân trái', 'Đánh đầu'], fontsize=10)
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Display the plot
        plt.show()

def kientao():
    if check_file_selected("Mở biểu đồ"):
        # Sort the data by Assists and select the top 10 players
        top_10_assists = data.nlargest(10, 'Assists')[['Name', 'Assists']]

        # Plotting the bar chart
        plt.figure(figsize=(12, 6))
        plt.barh(top_10_assists['Name'], top_10_assists['Assists'], color='skyblue', edgecolor='black')

        # Adding titles and labels
        plt.title('Top 10 Cầu Thủ Kiến Tạo Nhiều Nhất', fontsize=16)
        plt.xlabel('Số Kiến Tạo', fontsize=12)
        plt.ylabel('Cầu Thủ', fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Adding annotations for the exact number of assists
        for index, value in enumerate(top_10_assists['Assists']):
            plt.text(value + 0.5, index, str(value), va='center', fontsize=10)

        # Show the plot
        plt.tight_layout()
        plt.show()

def hauve():
    if check_file_selected("Mở biểu đồ"):    
        # Filter only defenders (e.g., based on Position column)
        defenders = data[data['Position'].str.contains('Defender', na=False)]

        # Sort defenders by Tackles and select the top 10
        top_10_defenders = defenders.nlargest(10, 'Tackles')[['Name', 'Tackles']]

        # Plotting the bar chart
        plt.figure(figsize=(12, 6))
        plt.barh(top_10_defenders['Name'], top_10_defenders['Tackles'], color='lightgreen', edgecolor='black')

        # Adding titles and labels
        plt.title('Top 10 Hậu Vệ Tắc Bóng Nhiều Nhất', fontsize=16, color = 'red')
        plt.xlabel('Số Lần Tắc Bóng', fontsize=12)
        plt.ylabel('Cầu Thủ', fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.gca().invert_yaxis()  # Invert y-axis to display the highest value on top
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Adding annotations for the exact number of tackles
        for index, value in enumerate(top_10_defenders['Tackles']):
            plt.text(value + 0.5, index, str(value), va='center', fontsize=10)

        # Show the plot
        plt.tight_layout()
        plt.show()

def thephat_club():
    if check_file_selected("Mở biểu đồ"):    
        # Nhóm dữ liệu theo câu lạc bộ và tính tổng số thẻ vàng, thẻ đỏ
        club_cards = data.groupby('Club')[['Yellow cards', 'Red cards']].sum()

        # Sắp xếp các câu lạc bộ theo tổng số thẻ vàng và thẻ đỏ giảm dần
        club_cards['Total cards'] = club_cards['Yellow cards'] + club_cards['Red cards']
        club_cards = club_cards.sort_values(by='Total cards', ascending=False)

        # Tạo biểu đồ
        plt.figure(figsize=(12, 10))
        yellow_bars = plt.barh(club_cards.index, club_cards['Yellow cards'], color='#FFD700', edgecolor='black', label='Yellow cards')
        red_bars = plt.barh(club_cards.index, club_cards['Red cards'], color='#FF4500', edgecolor='black', label='Red cards', left=club_cards['Yellow cards'])

        # Thêm số liệu trên từng cột
        for index, (yellow, red) in enumerate(zip(club_cards['Yellow cards'], club_cards['Red cards'])):
            plt.text(yellow / 2, index, str(int(yellow)), ha='center', va='center', fontsize=10, color='black')
            plt.text(yellow + red / 2, index, str(int(red)), ha='center', va='center', fontsize=10, color='white')

        # Thêm nhãn và tiêu đề
        plt.title('Số Thẻ Phạt của Từng Câu Lạc Bộ', fontsize=16, color='red')
        plt.xlabel('Số Lượng Thẻ', fontsize=12)
        plt.ylabel('Câu Lạc Bộ', fontsize=12)
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Tối ưu bố cục
        plt.tight_layout()
        plt.show()

def gk_best():
    if check_file_selected("Mở biểu đồ"):    
        # Lọc các cầu thủ có vị trí là thủ môn và sắp xếp theo số lần giữ sạch lưới
        thu_mon = data[data['Position'] == 'Goalkeeper']
        top_10_thu_mon = thu_mon.sort_values(by='Clean sheets', ascending=False).head(10)
        
        # Tạo biểu đồ
        plt.figure(figsize=(10, 6))
        bars = plt.barh(top_10_thu_mon['Name'], top_10_thu_mon['Clean sheets'], color='skyblue')
        plt.xlabel('Số lần giữ sạch lưới', fontsize=12)
        plt.ylabel('Thủ môn', fontsize=12)
        plt.title('Top 10 thủ môn giữ sạch lưới nhiều nhất', fontsize=14)
        plt.gca().invert_yaxis()  # Đảo ngược trục Y để thủ môn tốt nhất ở trên cùng

        # Thêm nhãn hiển thị số liệu trên mỗi thanh
        for bar in bars:
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                    f'{int(bar.get_width())}', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.show()

#______________________________________________________________ M E N U _________________________________________________________________________

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Thống kê cầu thủ giải Ngoại Hạng Anh")
root.geometry("1280x768")

# Thanh công cụ trên cùng
frame_top = tk.Frame(root, bg="#f0f0f0", height=50)
frame_top.pack(fill="x")
# Tìm kiếm dữ liệu
tk.Label(frame_top, text="Tìm kiếm:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=10)
search_entry = tk.Entry(frame_top, font=("Arial", 10))
search_entry.grid(row=1, column=1, padx=5, pady=10)
search_button = tk.Button(frame_top, text="Tìm kiếm", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                          command=lambda: search_data())
search_button.grid(row=1, column=2, padx=5, pady=10)

# Lọc dữ liệu
tk.Label(frame_top, text="Cột:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=10)
column_combobox = ttk.Combobox(frame_top, values=[], font=("Arial", 10))
column_combobox.grid(row=0, column=1, padx=5, pady=10)

tk.Label(frame_top, text="Điều kiện:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=10)
condition_combobox = ttk.Combobox(frame_top, values=["=", ">", "<", "contains"], font=("Arial", 10))
condition_combobox.grid(row=0, column=3, padx=5, pady=10)

tk.Label(frame_top, text="Giá trị:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=10)
value_entry = tk.Entry(frame_top, font=("Arial", 10))
value_entry.grid(row=0, column=5, padx=5, pady=10)

btn_apply_filter = tk.Button(frame_top, text="Áp dụng lọc", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=lambda: apply_filter())
btn_apply_filter.grid(row=0, column=6, padx=5, pady=10)

# Phần chính giữa giao diện
frame_middle = tk.Frame(root)
frame_middle.pack(fill="both", expand=True, padx=10, pady=10)

# Các nút chức năng
frame_buttons = tk.Frame(frame_middle, bg="#e0f7fa", padx=10, pady=10)
frame_buttons.pack(side="left", fill="y")
# Nút chọn file
chon_file = tk.Button(frame_buttons, text="Chọn file CSV", bg="yellow", fg="black", font=("Arial", 10, "bold"), command=open_file, height=2)
chon_file.pack(fill="x", pady=5)
# Nút chỉnh sửa dữ liệu
chinh_data = tk.Button(frame_buttons, text="Chỉnh sửa dữ liệu", bg="orange", fg="white", font=("Arial", 10, "bold"), command=edit_row, height=2)
chinh_data.pack(fill="x", pady=5)
# Nút thêm dữ liệu mới
tao_data = tk.Button(frame_buttons, text="Thêm dữ liệu mới", bg="green", fg="white", font=("Arial", 10, "bold"), command=add_new_data, height=2)
tao_data.pack(fill="x", pady=5)
# Nút xóa dòng dữ liệu
xoa_dong = tk.Button(frame_buttons, text="Xóa dòng dữ liệu", bg="red", fg="white", font=("Arial", 10, "bold"), command=delete_row, height=2)
xoa_dong.pack(fill="x", pady=5)

btn_bd_2 = tk.Button(frame_buttons, text="Top 25 Cầu Thủ Ghi Bàn Nhiều Nhất", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= cauthu_scored )
btn_bd_2.pack(fill="x", pady=5)

btn_bd_7 = tk.Button(frame_buttons, text="Top 10 Hậu Vệ Tắc Bóng Nhiều Nhất", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= hauve )
btn_bd_7.pack(fill="x", pady=5)

btn_bd_4 = tk.Button(frame_buttons, text="Top 10 quốc gia theo tổng số bàn thắng ghi được", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= quocgia_scored )
btn_bd_4.pack(fill="x", pady=5)

btn_bd_6 = tk.Button(frame_buttons, text="Top 10 Cầu Thủ Kiến Tạo Nhiều Nhất", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= kientao )
btn_bd_6.pack(fill="x", pady=5)

btn_bd_9 = tk.Button(frame_buttons, text="Top 10 thủ môn giữ sạch lưới nhiều nhất", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= gk_best )
btn_bd_9.pack(fill="x", pady=5)

btn_bd_1 = tk.Button(frame_buttons, text="Tỷ lệ quốc tịch của các cầu thủ", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= country )
btn_bd_1.pack(fill="x", pady=5)

btn_bd_3 = tk.Button(frame_buttons, text="Mối quan hệ giữa tuổi và số lần thi đấu", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= age )
btn_bd_3.pack(fill="x", pady=5)

btn_bd_5 = tk.Button(frame_buttons, text="Bàn Thắng Theo Từng CLB", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= banthang )
btn_bd_5.pack(fill="x", pady=5)

btn_bd_8 = tk.Button(frame_buttons, text="Số Thẻ Phạt của Từng Câu Lạc Bộ", bg="#4FC3F7", fg="white", font=("Arial", 10, "bold"), command= thephat_club )
btn_bd_8.pack(fill="x", pady=5)

# NÚT PHÂN TRANG
# Khung điều hướng
navigation_frame = tk.Frame(root)
navigation_frame.pack(side="bottom", fill="x", pady=5)

# Nút back
btn_previous = tk.Button(navigation_frame, text="<< Previous", command=go_to_previous_page)
btn_previous.pack(side="left", padx=10)

# Trạng thái trang
page_status_label = tk.Label(navigation_frame, text="Trang 1/1")
page_status_label.pack(side="left", padx=10)

# Nút next
btn_next = tk.Button(navigation_frame, text="Next >>", command=go_to_next_page)
btn_next.pack(side="left", padx=10)

# KHU VỰC TREEVIEW
frame_display = tk.Frame(frame_middle, bg="white", relief="sunken", bd=1)
frame_display.pack(side="right", fill="both", expand=True)

root.mainloop()