// MAIN PROGRAM //

FloatTable q_data;
int[] steps;

float[] dataMin;
float[] dataMax;

float ulc_x, ulc_y;
float lrc_x, lrc_y;
float divisions_h = 5;
float divisions_v = 12;

int graph_period = 1;

PFont plotFont;
String data_file;

int ms_since_last_refresh;
int ms_til_refresh = 30000;

void setup()
{
  size(window.innerWidth, window.innerHeight);

  data_file = "../../queue_data/Total_usage.csv";
  refreshData();
  ms_since_last_refresh = 0;

  ulc_x = 80;
  lrc_x = width - 60;
  ulc_y = 30;
  lrc_y = height - 60;
  
  plotFont = createFont("SansSerif", 20);
  textFont(plotFont);
  
  smooth();
}

void draw()
{
  background(#ffffff);
  
  float hx, hy, lx, ly;
  float y_span = (lrc_y - ulc_y);
  float bevel = 80;
  y_span -= 2 * bevel;
  
  // Waiting
  hx = ulc_x; hy = ulc_y;
  lx = lrc_x; ly = ulc_y + y_span * 0.34;
  noStroke();
  drawAxisTitles("Waiting", hx, hy, lx, ly);
  
  drawVAxisLabels(0, hx, hy, lx, ly);
  drawVAxisLines(0, hx, hy, lx, ly);
  
  drawHAxisLabels(0, hx, hy, lx, ly);
  drawHAxisLines(0, hx, hy, lx, ly);
  
  noFill();
  stroke(#C15679);
  drawCurve(0, hx, hy, lx, ly);

  // Running
  hx = ulc_x; hy = ulc_y + y_span * 0.34 + bevel;
  lx = lrc_x; ly = ulc_y + y_span * 0.67 + bevel;
  noStroke();
  drawAxisTitles("Running", hx, hy, lx, ly);
  
  drawVAxisLabels(1, hx, hy, lx, ly);
  drawVAxisLines(1, hx, hy, lx, ly);
  
  drawHAxisLabels(1, hx, hy, lx, ly);
  drawHAxisLines(1, hx, hy, lx, ly);
  
  noFill();
  stroke(#79C156);
  drawCurve(1, hx, hy, lx, ly);
  
  // Done
  hx = ulc_x; hy = ulc_y + y_span * 0.67 + 2*bevel;
  lx = lrc_x; ly = lrc_y;
  noStroke();
  drawAxisTitles("Done", hx, hy, lx, ly);
  
  drawVAxisLabels(2, hx, hy, lx, ly);
  drawVAxisLines(2, hx, hy, lx, ly);
  
  drawHAxisLabels(2, hx, hy, lx, ly);
  drawHAxisLines(2, hx, hy, lx, ly);
  
  noFill();
  stroke(#5679C1);
  drawCurve(2, hx, hy, lx, ly);
  
  // Update data if necessary
  int current_ms = millis();
  if( (current_ms - ms_since_last_refresh) > ms_til_refresh )
  {
    refreshData();
    ms_since_last_refresh = current_ms;
  }
}

void refreshData()
{
  q_data = new FloatTable(data_file);
  steps = int(q_data.getRowNames());
  
  dataMin = new float[q_data.getColumnCount()];
  dataMax = new float[q_data.getColumnCount()];
  interval_h = new float[q_data.getColumnCount()];
  interval_v = new float[q_data.getColumnCount()];
  
  for(int i = 0; i < 3; ++i)
  {
    float curMin = q_data.getColumnMin(i);
    float curMax = q_data.getColumnMax(i);
    if(curMin == curMax)
      curMax = 1;
    
    dataMin[i] = 0;
    dataMax[i] = roundToNearest((int)curMax, (int)divisions_h);
    interval_h[i] = dataMax[i] / divisions_h;
    interval_v[i] = roundToNearest(steps.length, divisions_v) / divisions_v;
  }

  redraw();
}

int roundToNearest(int num, int multi)
{
  if(multi == 0)
    return num;
  int rem = num % multi;
  if(rem == 0)
    return num;
  return num + multi - rem;
}

void drawCurve(int col, float hx, float hy, float lx, float ly)
{
  strokeWeight(1.5);

  beginShape();
  for(int row = 0; row < q_data.getRowCount(); row++)
  {
    if(q_data.isValid(row, col))
    {
      float value = q_data.getFloat(row, col);
      float x = map(steps[row], steps[0], steps[steps.length-1], lx, hx);
      float y = map(value, dataMin[col], dataMax[col], ly, hy);

      vertex(x, y);
      if((row == 0) || (row == q_data.getRowCount() - 1))
      {
        vertex(x, y);
      }
    }
  }
  
  endShape();
}

void drawAxisTitles(String label, float hx, float hy, float lx, float ly)
{
  fill(#000000);
  textSize(13);
  textLeading(15);
  
  float labelX = hx - 55;
  float labelY = ly + 40;
  
  textAlign(CENTER, CENTER);
  
  pushMatrix();
  translate(labelX, (ly + hy) / 2);
  rotate(-HALF_PI);
  text(label, 0, 0);
  popMatrix();
  
  textAlign(CENTER);

  text("Time (hour offset)", (hx + lx) / 2, labelY);

}

void drawVAxisLabels(int col, float hx, float hy, float lx, float ly)
{
  fill(#000000);
  textSize(10);
  textAlign(CENTER, TOP);
  
  // Mark Vertical intervals
  stroke(#7f7f7f);
  strokeWeight(1);
  
  int hour_offset = 0;
  for(int row = 0; row <= q_data.getRowCount()+1; row++)
  {
    if(row % interval_v[col] == 0)
    {
      float x = map(row, 0, q_data.getRowCount()+1, lx, hx);
      text(-hour_offset, x, ly + 10);      
      line(x, ly + 6, x, ly);
      hour_offset += 6;
    }
  }
}

void drawVAxisLines(int col, float hx, float hy, float lx, float ly)
{  // Mark Vertical intervals
  stroke(#bfbfbf);
  strokeWeight(1);
    
  for(int row = 0; row <= q_data.getRowCount()+1; row++)
  {
    if(row % interval_v[col] == 0)
    {
      float x = map(row, 0, q_data.getRowCount()+1, lx, hx);
      line(x, ly, x, hy);
    }
  }

}

void drawHAxisLabels(int col, float hx, float hy, float lx, float ly)
{
  fill(#000000);
  textSize(10);
  textAlign(RIGHT, CENTER);
  
  // Mark Horizontal intervals
  stroke(#7f7f7f);
  strokeWeight(1);
  
  for(float v = dataMin[col]; v <= dataMax[col]; v += interval_h[col])
  {
    if(v % interval_h[col] == 0)
    {
      float y = map(v, dataMin[col], dataMax[col], ly, hy);
      if(v == dataMin)
      {
        textAlign(RIGHT);
      } else if(v == dataMax[col]) {
        textAlign(RIGHT, CENTER);
      } else {
        textAlign(RIGHT, CENTER);
      }
      
      text(floor(v), hx - 12, y);
      line(hx - 6, y, hx, y);
    }

  }
}

void drawHAxisLines(int col, float hx, float hy, float lx, float ly)
{
  // Mark Horizontal intervals
  stroke(#bfbfbf);
  strokeWeight(1);
    
  for(float v = dataMin[col]; v <= dataMax[col]; v += interval_h[col])
  {
    if(v % interval_h[col] == 0)
    {
      float y = map(v, dataMin[col], dataMax[col], ly, hy);
      line(hx, y, lx, y);        
    }

  }

}

// CLASSES //

class FloatTable {
  int rowCount;
  int columnCount;
  float[][] data;
  String[] rowNames;
  String[] columnNames;
  
  
  FloatTable(String filename) {
    load(filename);
  }

  void load(filename) {
    String[] rows = loadStrings(filename);
    if(rows == null){
      println("Data is null");
    }
    
    String[] columns = split(rows[0], ",");
    columnNames = subset(columns, 1); // upper-left corner ignored
    scrubQuotes(columnNames);
    columnCount = columnNames.length;

    rowNames = new String[rows.length-1];
    data = new float[rows.length-1][];

    // start reading at row 1, because the first row was only the column headers
    for (int i = 1; i < rows.length; i++) {
      if (trim(rows[i]).length() == 0) {
        continue; // skip empty rows
      }
      if (rows[i].startsWith("#")) {
        continue;  // skip comment lines
      }

      // split the row on the tabs
      String[] pieces = split(rows[i], ",");
      scrubQuotes(pieces);
      
      // copy row title
      rowNames[rowCount] = pieces[0];
      // copy data into the table starting at pieces[1]
      data[rowCount] = parseFloat(subset(pieces, 1));

      // increment the number of valid rows found so far
      rowCount++;      
    }
    // resize the 'data' array as necessary
    data = (float[][]) subset(data, 0, rowCount);
  }
  
  
  void scrubQuotes(String[] array) {
    for (int i = 0; i < array.length; i++) {
      if (array[i].length() > 2) {
        // remove quotes at start and end, if present
        if (array[i].startsWith("\"") && array[i].endsWith("\"")) {
          array[i] = array[i].substring(1, array[i].length() - 1);
        }
      }
      // make double quotes into single quotes
      array[i] = array[i].replaceAll("\"\"", "\"");
    }
  }
  
  
  int getRowCount() {
    return rowCount;
  }
  
  
  String getRowName(int rowIndex) {
    return rowNames[rowIndex];
  }
  
  
  String[] getRowNames() {
    return rowNames;
  }

  
  // Find a row by its name, returns -1 if no row found. 
  // This will return the index of the first row with this name.
  // A more efficient version of this function would put row names
  // into a Hashtable (or HashMap) that would map to an integer for the row.
  int getRowIndex(String name) {
    for (int i = 0; i < rowCount; i++) {
      if (rowNames[i].equals(name)) {
        return i;
      }
    }
    //println("No row named '" + name + "' was found");
    return -1;
  }
  
  
  // technically, this only returns the number of columns 
  // in the very first row (which will be most accurate)
  int getColumnCount() {
    return columnCount;
  }
  
  
  String getColumnName(int colIndex) {
    return columnNames[colIndex];
  }
  
  
  String[] getColumnNames() {
    return columnNames;
  }


  float getFloat(int rowIndex, int col) {
    // Remove the 'training wheels' section for greater efficiency
    // It's included here to provide more useful error messages
    
    // begin training wheels
    if ((rowIndex < 0) || (rowIndex >= data.length)) {
      throw new RuntimeException("There is no row " + rowIndex);
    }
    if ((col < 0) || (col >= data[rowIndex].length)) {
      throw new RuntimeException("Row " + rowIndex + " does not have a column " + col);
    }
    // end training wheels
    
    return data[rowIndex][col];
  }
  
  
  boolean isValid(int row, int col) {
    if (row < 0) return false;
    if (row >= rowCount) return false;
    //if (col >= columnCount) return false;
    if (col >= data[row].length) return false;
    if (col < 0) return false;
    return (data[row][col] != NaN);
  }
  
  
  float getColumnMin(int col) {
    float m = 0xFFFFFF;
    for (int i = 0; i < rowCount; i++) {
      if (data[i][col] != NaN) {
        if (data[i][col] < m) {
          m = data[i][col];
        }
      }
    }
    return m;
  }

  
  float getColumnMax(int col) {
    float m = -0xFFFFFF;
    for (int i = 0; i < rowCount; i++) {
      if (isValid(i, col)) {
        if (data[i][col] > m) {
          m = data[i][col];
        }
      }
    }
    return m;
  }

}
