import io
import xlsxwriter


def make_kpo(data):
	output = io.BytesIO()

	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet()
	worksheet.hide_gridlines(2)

	worksheet.set_column('B:B', 25)
	worksheet.set_column('C:C', 30)
	worksheet.set_column('D:D', 25)
	worksheet.set_column('E:E', 25)
	worksheet.set_column('F:F', 20)
	worksheet.set_row(15, 40)
	worksheet.set_row(18, 30)
	worksheet.set_row(19, 30)

	format = {'align': 'right'}
	format_align_right = workbook.add_format(format)
	format = {'bottom': 1}
	format_border_down = workbook.add_format(format)
	format = {'bold': 1, 'align': 'center'}
	title_format = workbook.add_format(format)
	format = {'border': 1, 'align': 'center'}
	head_format = workbook.add_format(format)
	format = {'border': 1, 'align': 'center', 'text_wrap': 1}
	row_format = workbook.add_format(format)

	worksheet.write('B2', 'Obrazac KPO')
	worksheet.write('B4', 'PIB')
	worksheet.merge_range('C4:E4', data['pib'], format_border_down)
	worksheet.write('B5', 'Obveznik')
	worksheet.merge_range('C5:E5', data['full_name'], format_border_down)
	worksheet.write(
		'C6', '(ime i prezime poreskog obveznika)', format_border_down
	)
	worksheet.write('B7', 'Firma - radnje')
	worksheet.merge_range('C7:E7', data['company_name'], format_border_down)
	worksheet.write('B8', 'Sedište')
	worksheet.merge_range('C8:E8', data['company_address'], format_border_down)
	worksheet.write('C9', '(adresa)')
	worksheet.write('B10', 'Šifra poreskog obveznika')
	worksheet.merge_range('C10:E10', data['reg_no'], format_border_down)
	worksheet.write('B11', 'Šifra delatnosti')
	worksheet.merge_range(
		'C11:E11',
		data['company_activity_code'],
		format_border_down
	)

	worksheet.write('F2', 'KPO', format_align_right)

	worksheet.write(
		'D16',
		'KNJIGA O OSTVARENOM PROMETU\nPAUŠALNO OPOREZOVANIH OBVEZNIKA',
		title_format
	)

	worksheet.merge_range('B19:B20', "Redni\nbroj", head_format)
	worksheet.merge_range('C19:C20', "Datum i opis knjiženja", head_format)
	worksheet.merge_range('D19:E19', "Prihod od delatnosti", head_format)
	worksheet.write('D20', "od prodaje prizvoda", head_format)
	worksheet.write('E20', "od izvršenih uslouga", head_format)
	worksheet.merge_range(
		'F19:F20',
		"SVEGA\nPRIHODI OD\nDELATNOSTI\n(3 + 4)",
		head_format
	)

	worksheet.write('B21', "1", head_format)
	worksheet.write('C21', "2", head_format)
	worksheet.write('D21', "3", head_format)
	worksheet.write('E21', "4", head_format)
	worksheet.write('F21', "5", head_format)

	col, row = 1, 21
	c_row = row
	for row_data in data['rows']:
		c_col = col
		worksheet.set_row(c_row, 30)
		for i in range(len(row_data)):
			worksheet.write(c_row, c_col, str(row_data[i]), row_format)
			c_col += 1
		c_row += 1

	workbook.close()
	output.seek(0)

	return output
