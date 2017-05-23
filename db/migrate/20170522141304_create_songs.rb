class CreateSongs < ActiveRecord::Migration[5.0]
  def change
    create_table :songs do |t|
      t.string :name
      t.string :site
      t.string :description
      t.references :artist, foreign_key: true
      t.references :album, foreign_key: true
    end
  end
end
